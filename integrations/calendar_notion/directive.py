"""
integrations/calendar_notion/directive.py
──────────────────────────────────────────
Calendar directive for Notion integration.
Provides all calendar-related tools and system prompt.
"""
from typing import List

from integrations.base import Directive, Tool, CalendarIntegration
from .tools import (
    QueryEventsToolNotion,
    CreateEventToolNotion,
    UpdateEventToolNotion,
    DeleteEventToolNotion,
)

CALENDAR_SYSTEM_PROMPT = """\
Tu nombre es LushJr.
Eres un asistente personal experto en gestión de calendario.

Tu responsabilidad es ayudar al usuario a gestionar su calendario de forma eficiente.
Tienes acceso a las siguientes herramientas:
- query_events: Buscar eventos en un rango de fechas
- create_event: Crear un nuevo evento
- update_event: Modificar un evento existente
- delete_event: Eliminar un evento

Instrucciones:
1. Cuando el usuario pregunta por eventos, usa query_events con rango apropiado
2. Cuando el usuario quiere crear un evento, usa create_event
3. Cuando el usuario quiere modificar un evento, usa update_event
4. Cuando el usuario quiere eliminar, usa delete_event
5. Para eventos relativos (mañana, siguiente semana, etc.), calcula las fechas apropiadas
6. Si el usuario menciona "esta semana", asume desde hoy hasta 6 días después
7. Responde siempre en español
8. Sé amable y útil en tus respuestas
"""


class CalendarDirective(Directive):
    """Directive that provides calendar management tools."""
    
    def __init__(self, calendar_integration: CalendarIntegration):
        self.calendar = calendar_integration
        self._tools = [
            QueryEventsToolNotion(calendar_integration),
            CreateEventToolNotion(calendar_integration),
            UpdateEventToolNotion(calendar_integration),
            DeleteEventToolNotion(calendar_integration),
        ]
    
    def get_tools(self) -> List[Tool]:
        """Return list of available calendar tools."""
        return self._tools
    
    def get_system_prompt(self) -> str:
        """Return system prompt for calendar assistant."""
        return CALENDAR_SYSTEM_PROMPT
