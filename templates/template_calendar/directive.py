"""
integrations/template_calendar/directive.py
───────────────────────────────────────────
Template calendar directive implementation.

This template demonstrates how to create a directive for your calendar
integration. A directive bundles tools and a system prompt.

You can:
- Reuse the CalendarDirective from the Notion plugin if your tools
  have the same names and interfaces (query_events, create_event,
  update_event, delete_event, chat).
- Or create your own directive, as shown below, which creates tools
  that wrap your integration's methods.

For simplicity, this template creates a directive with basic tools
that mirror the calendar integration's methods.
"""

from integrations.base import CalendarIntegration, Directive, Tool, ToolResult


class QueryEventsTool(Tool):
    """Tool to query events from the calendar integration."""
    def __init__(self, calendar: CalendarIntegration):
        self._calendar = calendar

    @property
    def name(self) -> str:
        return "query_events"

    @property
    def description(self) -> str:
        return "List events in a date range."

    @property
    def params(self) -> dict:
        return {
            "date_start": {"type": "string", "description": "Start date (YYYY-MM-DD)", "required": True},
            "date_end":   {"type": "string", "description": "End date (YYYY-MM-DD)",   "required": True},
        }

    def execute(self, params: dict) -> ToolResult:
        try:
            events = self._calendar.query_events(
                date_start=params["date_start"],
                date_end=params["date_end"],
            )
            # Convert events to dictionaries for the ToolResult data
            events_data = [
                {
                    "id": e.id,
                    "title": e.title,
                    "date_start": e.date_start,
                    "date_end": e.date_end,
                    "time_start": e.time_start,
                    "time_end": e.time_end,
                    "location": e.location,
                    "description": e.description,
                }
                for e in events
            ]
            return ToolResult(
                success=True,
                message=f"Found {len(events)} events.",
                data={"events": events_data},
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Error querying events: {e}")


class CreateEventTool(Tool):
    """Tool to create an event via the calendar integration."""
    def __init__(self, calendar: CalendarIntegration):
        self._calendar = calendar

    @property
    def name(self) -> str:
        return "create_event"

    @property
    def description(self) -> str:
        return "Create a new calendar event."

    @property
    def params(self) -> dict:
        return {
            "title":       {"type": "string", "description": "Event title",           "required": True},
            "date_start":  {"type": "string", "description": "Start date (YYYY-MM-DD)", "required": True},
            "date_end":    {"type": "string", "description": "End date (YYYY-MM-DD)",   "required": False},
            "time_start":  {"type": "string", "description": "Start time (HH:MM)",      "required": False},
            "time_end":    {"type": "string", "description": "End time (HH:MM)",        "required": False},
            "location":    {"type": "string", "description": "Event location",          "required": False},
            "description": {"type": "string", "description": "Event description",       "required": False},
        }

    def execute(self, params: dict) -> ToolResult:
        try:
            event = self._calendar.create_event(
                title=params["title"],
                date_start=params["date_start"],
                date_end=params.get("date_end"),
                time_start=params.get("time_start"),
                time_end=params.get("time_end"),
                location=params.get("location"),
                description=params.get("description"),
            )
            return ToolResult(
                success=True,
                message=f"Event created: {event.title}",
                data={
                    "id": event.id,
                    "title": event.title,
                    "date_start": event.date_start,
                    "date_end": event.date_end,
                    "time_start": event.time_start,
                    "time_end": event.time_end,
                    "location": event.location,
                    "description": event.description,
                },
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Error creating event: {e}")


class UpdateEventTool(Tool):
    """Tool to update an event via the calendar integration."""
    def __init__(self, calendar: CalendarIntegration):
        self._calendar = calendar

    @property
    def name(self) -> str:
        return "update_event"

    @property
    def description(self) -> str:
        return "Update an existing calendar event."

    @property
    def params(self) -> dict:
        return {
            "event_id":    {"type": "string", "description": "Event ID",               "required": True},
            "title":       {"type": "string", "description": "New title",               "required": False},
            "date_start":  {"type": "string", "description": "New start date (YYYY-MM-DD)", "required": False},
            "date_end":    {"type": "string", "description": "New end date (YYYY-MM-DD)",   "required": False},
            "time_start":  {"type": "string", "description": "New start time (HH:MM)",      "required": False},
            "time_end":    {"type": "string", "description": "New end time (HH:MM)",        "required": False},
            "location":    {"type": "string", "description": "New location",              "required": False},
            "description": {"type": "string", "description": "New description",         "required": False},
        }

    def execute(self, params: dict) -> ToolResult:
        try:
            event = self._calendar.update_event(
                event_id=params["event_id"],
                title=params.get("title"),
                date_start=params.get("date_start"),
                date_end=params.get("date_end"),
                time_start=params.get("time_start"),
                time_end=params.get("time_end"),
                location=params.get("location"),
                description=params.get("description"),
            )
            return ToolResult(
                success=True,
                message=f"Event updated: {event.title}",
                data={
                    "id": event.id,
                    "title": event.title,
                    "date_start": event.date_start,
                    "date_end": event.date_end,
                    "time_start": event.time_start,
                    "time_end": event.time_end,
                    "location": event.location,
                    "description": event.description,
                },
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Error updating event: {e}")


class DeleteEventTool(Tool):
    """Tool to delete an event via the calendar integration."""
    def __init__(self, calendar: CalendarIntegration):
        self._calendar = calendar

    @property
    def name(self) -> str:
        return "delete_event"

    @property
    def description(self) -> str:
        return "Delete a calendar event."

    @property
    def params(self) -> dict:
        return {
            "event_id": {"type": "string", "description": "Event ID", "required": True},
        }

    def execute(self, params: dict) -> ToolResult:
        try:
            self._calendar.delete_event(event_id=params["event_id"])
            return ToolResult(
                success=True,
                message=f"Event deleted.",
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Error deleting event: {e}")


class ChatTool(Tool):
    """Tool for general chat (no action)."""
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "chat"

    @property
    def description(self) -> str:
        return "General conversation (no calendar action)."

    @property
    def params(self) -> dict:
        return {}  # No parameters

    def execute(self, params: dict) -> ToolResult:
        # This tool should never be executed directly; the AI provider
        # handles chat separately. We return a placeholder.
        return ToolResult(success=True, message="Chat tool executed.")


# ──────────────────────────────────────────────────────────────────────────────
# Directive
# ──────────────────────────────────────────────────────────────────────────────

class TemplateCalendarDirective(Directive):
    """
    A directive that bundles the calendar tools with a system prompt.

    You can customize the system prompt by passing a custom string to
    the constructor, or by overriding the system_prompt() method.
    """

    def __init__(
        self,
        calendar: CalendarIntegration,
        system_prompt: str | None = None,
    ) -> None:
        self._tools: list[Tool] = [
            QueryEventsTool(calendar),
            CreateEventTool(calendar),
            UpdateEventTool(calendar),
            DeleteEventTool(calendar),
            ChatTool(),  # Optional: include chat tool
        ]
        self._system_prompt = system_prompt or (
            "You are a calendar assistant. Help the user manage their calendar events.\n"
            "Always reply in the same language the user writes in."
        )

    def tools(self) -> list[Tool]:
        return self._tools

    def system_prompt(self) -> str:
        return self._system_prompt


__all__ = ["TemplateCalendarDirective", "QueryEventsTool", "CreateEventTool", "UpdateEventTool", "DeleteEventTool", "ChatTool"]