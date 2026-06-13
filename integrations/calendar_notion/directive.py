"""
integrations/calendar_notion/directive.py
──────────────────────────────────────────
Calendar directive for Notion integration.
Provides all calendar-related tools and the system prompt.

El system prompt NO está definido aquí.
Vive en core/prompts.py — edita ese archivo para cambiar el comportamiento.
"""
from typing import List, Optional, TYPE_CHECKING

from core.prompts import render_calendar_system
from integrations.base import Directive, Tool, CalendarIntegration
from .tools import (
    QueryEventsToolNotion,
    CreateEventToolNotion,
    UpdateEventToolNotion,
    DeleteEventToolNotion,
    ChatTool,
)

if TYPE_CHECKING:
    from integrations.core_ai.provider import NvidiaAIProvider


class CalendarDirective(Directive):
    """Directive that provides calendar management tools."""

    def __init__(
        self,
        calendar_integration: CalendarIntegration,
        ai_provider: Optional["NvidiaAIProvider"] = None,
    ):
        self.calendar = calendar_integration
        self.ai_provider = ai_provider
        self._tools: List[Tool] = [
            QueryEventsToolNotion(calendar_integration),
            CreateEventToolNotion(calendar_integration),
            UpdateEventToolNotion(calendar_integration),
            DeleteEventToolNotion(calendar_integration),
        ]

        if ai_provider:
            self._tools.append(ChatTool(ai_provider))

    def get_tools(self) -> List[Tool]:
        return self._tools

    def get_system_prompt(self) -> str:
        """
        Returns the rendered calendar system prompt.
        Source of truth: core/prompts.py → PROMPTS.calendar_system
        """
        return render_calendar_system()