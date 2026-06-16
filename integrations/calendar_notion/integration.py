"""
integrations/calendar_notion/integration.py
────────────────────────────────────────────
CalendarIntegration backed by a Notion database.

Notion stores datetime as ISO-8601 strings; we expose them as plain
dates ("YYYY-MM-DD") and times ("HH:MM") so the rest of the code stays
platform-agnostic.

Fields are configurable so this works with any Notion database schema.
"""

import logging
from typing import Any

from notion_client import Client

from integrations.base import BaseIntegration, CalendarEvent

logger = logging.getLogger(__name__)


class NotionCalendarIntegration(BaseIntegration):
    """
    Reads and writes events in a Notion database.

    Parameters
    ----------
    token          : Notion integration token (NOTION_TOKEN).
    database_id    : Target database ID (DATABASE_ID).
    prop_*         : Notion property names — change these to match your schema.
    """

    def __init__(
        self,
        token:           str,
        database_id:     str,
        prop_title:      str = "Nombre",
        prop_date:       str = "Fecha",
        prop_time:       str = "Hora",
        prop_location:   str = "Lugar",
        prop_description:str = "Descripción",
    ) -> None:
        self._notion      = Client(auth=token)
        self._db_id       = database_id
        self._p_title     = prop_title
        self._p_date      = prop_date
        self._p_time      = prop_time
        self._p_location  = prop_location
        self._p_desc      = prop_description
        self._props       = self._fetch_db_props()

    # ──────────────────────────────────────────────────────────────────────
    # CalendarIntegration interface
    # ──────────────────────────────────────────────────────────────────────

    def query_events(self, date_start: str, date_end: str) -> list[CalendarEvent]:
        response = self._notion.databases.query(
            database_id=self._db_id,
            filter={
                "and": [
                    {"property": self._p_date, "date": {"on_or_after":  date_start}},
                    {"property": self._p_date, "date": {"on_or_before": date_end}},
                ]
            },
            sorts=[{"property": self._p_date, "direction": "ascending"}],
        )
        return [self._page_to_event(p) for p in response.get("results", [])]

    def create_event(
        self,
        title:       str,
        date_start:  str,
        date_end:    str | None = None,
        time_start:  str | None = None,
        time_end:    str | None = None,
        location:    str | None = None,
        description: str | None = None,
    ) -> CalendarEvent:
        page = self._notion.pages.create(
            parent={"database_id": self._db_id},
            properties=self._build_props(
                title, date_start, date_end, time_start, time_end, location, description
            ),
        )
        return self._page_to_event(page)

    def update_event(
        self,
        event_id:    str,
        title:       str | None = None,
        date_start:  str | None = None,
        date_end:    str | None = None,
        time_start:  str | None = None,
        time_end:    str | None = None,
        location:    str | None = None,
        description: str | None = None,
    ) -> CalendarEvent:
        current = self._page_to_event(self._notion.pages.retrieve(page_id=event_id))
        page = self._notion.pages.update(
            page_id=event_id,
            properties=self._build_props(
                title       or current.title,
                date_start  or current.date_start,
                date_end    or current.date_end,
                time_start  or current.time_start,
                time_end    or current.time_end,
                location    or current.location,
                description or current.description,
            ),
        )
        return self._page_to_event(page)

    def delete_event(self, event_id: str) -> None:
        """Archive the Notion page (equivalent to deletion)."""
        self._notion.pages.update(page_id=event_id, archived=True)

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────

    def _build_props(
        self,
        title:       str,
        date_start:  str,
        date_end:    str | None,
        time_start:  str | None,
        time_end:    str | None,
        location:    str | None,
        description: str | None,
    ) -> dict[str, Any]:
        """Build the Notion properties payload for create/update calls."""
        start = f"{date_start}T{time_start}:00" if time_start else date_start
        end: str | None = None
        if date_end or time_end:
            d   = date_end or date_start
            end = f"{d}T{time_end}:00" if time_end else d

        date_payload: dict[str, Any] = {"start": start}
        if end:
            date_payload["end"] = end

        props: dict[str, Any] = {
            self._p_title: {"title": [{"text": {"content": title}}]},
            self._p_date:  {"date":  date_payload},
        }

        if location and self._p_location in self._props:
            props[self._p_location] = {"rich_text": [{"text": {"content": location}}]}

        if description and self._p_desc in self._props:
            props[self._p_desc] = {"rich_text": [{"text": {"content": description}}]}

        if time_start and self._p_time in self._props:
            time_label = f"{time_start}–{time_end}" if time_end else time_start
            props[self._p_time] = {"rich_text": [{"text": {"content": time_label}}]}

        return props

    def _page_to_event(self, page: dict) -> CalendarEvent:
        """Convert a raw Notion page dict into a CalendarEvent."""
        props = page.get("properties", {})

        title_parts = props.get(self._p_title, {}).get("title", [])
        title       = title_parts[0]["plain_text"] if title_parts else "(no title)"

        date_obj  = props.get(self._p_date, {}).get("date") or {}
        raw_start = date_obj.get("start", "")
        raw_end   = date_obj.get("end")

        date_start, time_start = self._split_datetime(raw_start)
        date_end,   time_end   = self._split_datetime(raw_end) if raw_end else (None, None)

        loc_parts  = props.get(self._p_location, {}).get("rich_text", [])
        desc_parts = props.get(self._p_desc,     {}).get("rich_text", [])

        return CalendarEvent(
            id          = page.get("id", ""),
            title       = title,
            date_start  = date_start,
            date_end    = date_end,
            time_start  = time_start,
            time_end    = time_end,
            location    = loc_parts[0]["plain_text"]  if loc_parts  else None,
            description = desc_parts[0]["plain_text"] if desc_parts else None,
        )

    @staticmethod
    def _split_datetime(value: str) -> tuple[str, str | None]:
        """Split "2025-06-10T14:00:00" → ("2025-06-10", "14:00")."""
        if "T" in value:
            date_part, time_part = value.split("T", 1)
            return date_part, time_part[:5]
        return value, None

    def _fetch_db_props(self) -> set[str]:
        """Load available property names from the Notion database."""
        try:
            db = self._notion.databases.retrieve(self._db_id)
            return set(db.get("properties", {}).keys())
        except Exception as exc:
            logger.warning("Could not load database schema: %s", exc)
            return set()