"""
integrations/calendar_notion/directive.py (REFACTORED)
──────────────────────────────────────────────────────────
Directive that wires calendar tools to any DataIntegration backend.

KEY CHANGE: Uses DataIntegration instead of NotionCalendarIntegration
────────────────────────────────────────────────────────────────────

Now compatible with:
- Notion
- Google Calendar
- iCal
- Outlook
- Any custom backend

Customisation
-------------
- To change the bot's name or behavior, pass a custom system_prompt
  string to CalendarDirective.__init__().
- To add a new tool, instantiate it here and append to self._tools.
- DEFAULT_SYSTEM_PROMPT provides baseline instructions for the AI.
"""
from __future__ import annotations

from integrations.base import BaseDirective, Directive, Tool, DataIntegration
from .tools import (
    CreateEventTool,
    DeleteEventTool,
    QueryEventsTool,
    UpdateEventTool,
)

# ──────────────────────────────────────────────────────────────────────────────
# Default system prompt
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_SYSTEM_PROMPT = """\
Available tools:
- query_events  : List events in a date range.
- create_event  : Add a new event.
- update_event  : Modify an existing event.
- delete_event  : Remove an event.
- chat          : Answer general questions or have a conversation.

Guidelines:
- Use relative date keywords (today, tomorrow, this week…) when helpful.
- If the user asks to perform the same action on multiple items
  (e.g. "delete all events this month"), return one tool call per item.
- Prefer brevity in confirmations; expand only when the user asks.
"""


# ──────────────────────────────────────────────────────────────────────────────
# Directive
# ──────────────────────────────────────────────────────────────────────────────

class CalendarDirective(BaseDirective):
    """
    Groups all calendar tools and the system prompt.
    
    Works with ANY DataIntegration backend.

    Parameters
    ----------
    data_integration : DataIntegration
        Any backend that implements DataIntegration (Notion, Google Calendar, etc.)
    system_prompt : str | None
        Override the default prompt to change language, persona, etc.
    extra_tools : list[Tool] | None
        Additional Tool instances to register alongside the defaults.
    """

    def __init__(
        self,
        data_integration: DataIntegration,
        system_prompt: str | None = None,
        extra_tools: list[Tool] | None = None,
    ) -> None:
        tools = [
            QueryEventsTool(data_integration),
            CreateEventTool(data_integration),
            UpdateEventTool(data_integration),
            DeleteEventTool(data_integration),
        ]
        if extra_tools:
            tools.extend(extra_tools)

        # If a system_prompt is provided (e.g., from config), use it as base
        # and append the default calendar-specific prompt
        if system_prompt is not None:
            base_system_prompt = f"{system_prompt}\n\n{DEFAULT_SYSTEM_PROMPT}"
        else:
            base_system_prompt = DEFAULT_SYSTEM_PROMPT

        super().__init__(tools=tools, system_prompt=base_system_prompt)


__all__ = ["CalendarDirective", "DEFAULT_SYSTEM_PROMPT"]