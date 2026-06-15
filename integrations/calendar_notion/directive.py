"""
integrations/calendar_notion/directive.py
──────────────────────────────────────────
Directive that wires the Notion calendar tools together.

Customisation
-------------
- To change the bot's name or language, pass a custom system_prompt
  string to CalendarDirective.__init__().
- To add a new tool, instantiate it here and append to self._tools.
- DEFAULT_SYSTEM_PROMPT instructs the AI to detect the user's language and respond in the same language.
"""
from __future__ import annotations

from integrations.base import CalendarIntegration, Directive, Tool
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
You are LushJr, a personal calendar assistant.

Your responsibilities:
- Help the user manage their calendar events efficiently.
- Detect the language of the user's message and respond in that same language.
- Be concise, friendly, and proactive.

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

class CalendarDirective(Directive):
    """
    Groups all calendar tools and the system prompt.

    Parameters
    ----------
    calendar      : Any CalendarIntegration (Notion, Google, …).
    system_prompt : Override the default prompt to change language, persona, etc.
    extra_tools   : Additional Tool instances to register alongside the defaults.
    """

    def __init__(
        self,
        calendar:      CalendarIntegration,
        system_prompt: str | None = None,
        extra_tools:   list[Tool] | None = None,
    ) -> None:
        self._tools: list[Tool] = [
            QueryEventsTool(calendar),
            CreateEventTool(calendar),
            UpdateEventTool(calendar),
            DeleteEventTool(calendar),
        ]
        if extra_tools:
            self._tools.extend(extra_tools)

        self._system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    def tools(self) -> list[Tool]:
        return self._tools

    def system_prompt(self) -> str:
        return self._system_prompt