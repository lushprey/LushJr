"""
integrations/calendar_notion/tools.py (REFACTORED)
──────────────────────────────────────────────────────
Calendar tools that work with ANY DataIntegration backend.

KEY CHANGE: Uses DataIntegration instead of NotionCalendarIntegration
────────────────────────────────────────────────────────────────────

Now you can use these tools with:
- Notion
- Google Calendar
- iCal
- Outlook
- Any custom backend that implements DataIntegration

Each class implements Tool from integrations.base.
To add a new calendar action, create a new subclass here and register it 
in directive.py — no other file needs to change.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from integrations.base import Tool, ToolResult, DataIntegration, CalendarEvent

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Base Tool Class
# ──────────────────────────────────────────────────────────────────────────────

class BaseCalendarTool(Tool):
    """Base class for calendar tools to reduce boilerplate."""

    def __init__(self, data_integration: DataIntegration) -> None:
        """
        Initialize with a generic DataIntegration.
        
        Args:
            data_integration: Any DataIntegration backend (Notion, Google, etc.)
        """
        super().__init__()
        self._integration = data_integration

    def _resolve_date_param(self, param_value: str | None, default: str = "today") -> str | None:
        """Resolve a date parameter if it's not None."""
        if param_value is None:
            return None
        return _resolve_date(param_value)

    def _validate_required_params(self, params: dict[str, Any], required_fields: list[str]) -> str | None:
        """Validate required parameters and return error message if validation fails."""
        for field in required_fields:
            if not params.get(field):
                return f"❌ {field} is required."
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Date utilities
# ──────────────────────────────────────────────────────────────────────────────

def _resolve_date(value: str) -> str:
    """
    Convert a relative or natural-language date string to ISO-8601 (YYYY-MM-DD).

    Supports English and Spanish keywords:
      today / hoy, tomorrow / mañana, yesterday / ayer,
      this week / esta semana, this month / este mes.

    Falls back to the original string if it already looks like a date.
    Falls back to today's date and logs a warning if nothing matches.
    """
    today = datetime.now().date()
    v     = value.lower().strip()

    mapping = {
        ("hoy",         "today"):       lambda: today,
        ("mañana",      "tomorrow"):    lambda: today + timedelta(days=1),
        ("ayer",        "yesterday"):   lambda: today - timedelta(days=1),
    }

    for keywords, fn in mapping.items():
        if v in keywords:
            return fn().isoformat()

    if "semana" in v or "week" in v:
        days_left = (6 - today.weekday()) % 7 or 7
        return (today + timedelta(days=days_left)).isoformat()

    if "mes" in v or "month" in v:
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return end.isoformat()

    # Already ISO-8601?
    try:
        datetime.fromisoformat(value)
        return value
    except ValueError:
        pass

    logger.warning("Could not parse date %r — using today.", value)
    return today.isoformat()


def _fmt_event(event) -> str:
    """Format a CalendarEvent into a single-line summary."""
    time_part     = f" at {event.time_start}" if event.time_start else ""
    time_end_part = f"–{event.time_end}"       if event.time_end  else ""
    location_part = f"  📍 {event.location}"   if event.location  else ""
    return f"• **{event.title}** ({event.date_start}{time_part}{time_end_part}){location_part}"


# ──────────────────────────────────────────────────────────────────────────────
# Tools (now work with any DataIntegration backend)
# ──────────────────────────────────────────────────────────────────────────────

class QueryEventsTool(BaseCalendarTool):
    """Retrieve calendar events between two dates."""

    def __init__(self, data_integration: DataIntegration) -> None:
        super().__init__(data_integration)

    @property
    def name(self) -> str:
        return "query_events"

    @property
    def description(self) -> str:
        return "Retrieve calendar events between two dates."

    @property
    def params(self) -> dict:
        return {
            "date_start": {"type": "string", "description": "Start date (YYYY-MM-DD or relative like 'today')", "required": True},
            "date_end":   {"type": "string", "description": "End date   (YYYY-MM-DD or relative like 'this week')", "required": True},
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        date_start = self._resolve_date_param(params.get("date_start", "today"))
        date_end   = self._resolve_date_param(params.get("date_end",   "today"))

        if date_end < date_start:
            date_end = date_start

        # Use generic query interface
        events = self._integration.query({
            "date_start": date_start,
            "date_end": date_end,
        })

        if not events:
            return ToolResult(
                success=True,
                message=f"📅 No events found between {date_start} and {date_end}.",
                data={"events": []},
            )

        lines  = [f"📅 {len(events)} event(s) from {date_start} to {date_end}:"]
        lines += [_fmt_event(e) for e in events]
        return ToolResult(
            success=True,
            message="\n".join(lines),
            data={"events": [vars(e) for e in events]},
        )


class CreateEventTool(BaseCalendarTool):
    """Create a new calendar event."""

    def __init__(self, data_integration: DataIntegration) -> None:
        super().__init__(data_integration)

    @property
    def name(self) -> str:
        return "create_event"

    @property
    def description(self) -> str:
        return "Create a new calendar event."

    @property
    def params(self) -> dict:
        return {
            "title":       {"type": "string", "description": "Event title",                                     "required": True},
            "date_start":  {"type": "string", "description": "Start date (YYYY-MM-DD or relative)",             "required": True},
            "date_end":    {"type": "string", "description": "End date   (YYYY-MM-DD or relative)",             "required": False},
            "time_start":  {"type": "string", "description": "Start time HH:MM",                               "required": False},
            "time_end":    {"type": "string", "description": "End time   HH:MM",                               "required": False},
            "location":    {"type": "string", "description": "Event location",                                  "required": False},
            "description": {"type": "string", "description": "Event description or notes",                     "required": False},
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        title      = params.get("title")
        date_start = params.get("date_start")

        if not title or not date_start:
            return ToolResult(success=False, message="❌ title and date_start are required.")

        date_start = self._resolve_date_param(date_start)
        date_end   = self._resolve_date_param(params["date_end"]) if params.get("date_end") else None

        # Create generic CalendarEvent
        event = CalendarEvent(
            id="",  # Backend will assign ID
            title=title,
            date_start=date_start,
            date_end=date_end,
            time_start=params.get("time_start"),
            time_end=params.get("time_end"),
            location=params.get("location"),
            description=params.get("description"),
        )
        
        # Use generic create interface
        created_event = self._integration.create(event)
        
        return ToolResult(
            success=True,
            message=f"✅ Created: {_fmt_event(created_event)}",
            data={"event": vars(created_event)},
        )


class UpdateEventTool(BaseCalendarTool):
    """Update an existing calendar event."""

    def __init__(self, data_integration: DataIntegration) -> None:
        super().__init__(data_integration)

    @property
    def name(self) -> str:
        return "update_event"

    @property
    def description(self) -> str:
        return "Update an existing calendar event by its ID."

    @property
    def params(self) -> dict:
        return {
            "event_id":    {"type": "string", "description": "Page ID of the event",  "required": True},
            "title":       {"type": "string", "description": "New title",                    "required": False},
            "date_start":  {"type": "string", "description": "New start date",               "required": False},
            "date_end":    {"type": "string", "description": "New end date",                 "required": False},
            "time_start":  {"type": "string", "description": "New start time HH:MM",        "required": False},
            "time_end":    {"type": "string", "description": "New end time   HH:MM",        "required": False},
            "location":    {"type": "string", "description": "New location",                 "required": False},
            "description": {"type": "string", "description": "New description",              "required": False},
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        event_id = params.get("event_id")
        if not event_id:
            return ToolResult(success=False, message="❌ event_id is required.")

        # Resolve date params
        updates = {}
        for key in ["date_start", "date_end"]:
            if params.get(key):
                updates[key] = self._resolve_date_param(params[key])
        
        # Add other fields
        for key in ["title", "time_start", "time_end", "location", "description"]:
            if params.get(key):
                updates[key] = params[key]

        # Use generic update interface
        event = self._integration.update(event_id, updates)
        
        return ToolResult(
            success=True,
            message=f"✅ Updated: {_fmt_event(event)}",
            data={"event": vars(event)},
        )


class DeleteEventTool(BaseCalendarTool):
    """Delete (archive) a calendar event."""

    def __init__(self, data_integration: DataIntegration) -> None:
        super().__init__(data_integration)

    @property
    def name(self) -> str:
        return "delete_event"

    @property
    def description(self) -> str:
        return "Delete a calendar event by its ID."

    @property
    def params(self) -> dict:
        return {
            "event_id": {"type": "string", "description": "Page ID of the event to delete", "required": True},
        }

    def execute(self, params: dict[str, Any]) -> ToolResult:
        event_id = params.get("event_id")
        if not event_id:
            return ToolResult(success=False, message="❌ event_id is required.")

        # Use generic delete interface
        self._integration.delete(event_id)
        
        return ToolResult(success=True, message=f"🗑️ Deleted event {event_id}.")