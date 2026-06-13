"""
core/prompts.py
────────────────
Single source of truth for ALL prompts used in the bot.

To change any prompt, edit ONLY this file.
No other file needs to be touched — all AI providers and directives
consume prompts from here, regardless of implementation.

Structure:
  - PromptConfig: dataclass holding all prompt templates
  - PROMPTS: global singleton instance — edit this to change behavior
  - Helper functions for rendering templates with context
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
# PROMPT TEMPLATES
# Edit the strings inside PROMPTS (bottom of file) to change behavior.
# The dataclass here just defines the structure.
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PromptConfig:
    """
    Container for all prompt templates used by the bot.

    Fields with {placeholders} are rendered at runtime via render_*() helpers.
    Fields without placeholders are used as-is.
    """

    # ── Bot identity ─────────────────────────────────────────────────────────
    # Used in all prompts to give the bot a consistent persona.
    bot_name: str = "LushJr"
    bot_language: str = "español"

    # ── Intent detection (legacy / fallback JSON parsing) ────────────────────
    # Used by NvidiaAIProvider.detect_intent() and the JSON fallback in
    # call_with_tools(). Receives {fecha_hoy} and {dia_semana} at runtime.
    intent_system: str = """\
Tu nombre es {bot_name}.
Eres el cerebro de un asistente personal en Telegram conectado a un calendario.
Hoy es {fecha_hoy} ({dia_semana}).

Tu única tarea es analizar el mensaje del usuario y devolver un JSON con esta estructura exacta:

{{
  "accion": "consultar" | "crear" | "editar" | "eliminar" | "chat",
  "fecha_inicio": "YYYY-MM-DD",
  "fecha_fin": "YYYY-MM-DD",
  "hora_inicio": "HH:MM",
  "hora_fin": "HH:MM",
  "titulo": "nombre del evento",
  "lugar": "lugar del evento",
  "descripcion": "descripción del evento",
  "event_id": "id de notion si el usuario lo menciona",
  "respuesta_directa": "texto solo si accion es chat"
}}

Reglas:
- Incluye solo los campos relevantes al mensaje, omite los demás
- "consultar": el usuario pregunta por eventos
- "crear": el usuario quiere agendar, agregar o crear un evento
- "editar": el usuario quiere modificar un evento existente
- "eliminar": el usuario quiere borrar o cancelar un evento
- "chat": cualquier otra pregunta o conversación
- Para fechas relativas usa la fecha de hoy como referencia
- Para "esta semana" usa fecha_fin = hoy + 6 días
- Si el usuario dice "a las 3pm" → hora_inicio: "15:00"
- Si el usuario dice "de 2 a 4" → hora_inicio: "14:00", hora_fin: "16:00"
- SOLO devuelve el JSON, sin explicaciones ni markdown
"""

    # ── Tool-selection fallback (JSON mode) ──────────────────────────────────
    # Appended to the directive system prompt when function calling is not
    # available. {tool_descriptions} is injected at runtime.
    tool_selection_fallback: str = """\

Available tools:
{tool_descriptions}

Respond with ONLY a JSON object like this:
{{
  "tool": "tool_name_here",
  "params": {{"param1": "value1", "param2": "value2"}}
}}
"""

    # ── Calendar directive system prompt ─────────────────────────────────────
    # Passed to the AI as the system prompt for all calendar interactions.
    calendar_system: str = """\
Tu nombre es {bot_name}.
Eres un asistente personal experto en gestión de calendario.

Tu responsabilidad es ayudar al usuario a gestionar su calendario de forma eficiente.
Tienes acceso a las siguientes herramientas:
- query_events: Buscar eventos en un rango de fechas
- create_event: Crear un nuevo evento
- update_event: Modificar un evento existente
- delete_event: Eliminar un evento
- chat: Para cualquier pregunta o conversación que no sea sobre calendario

Instrucciones:
1. Cuando el usuario pregunta por eventos, usa query_events con rango apropiado
2. Cuando el usuario quiere crear un evento, usa create_event
3. Cuando el usuario quiere modificar un evento, usa update_event
4. Cuando el usuario quiere eliminar, usa delete_event
5. Para eventos relativos (mañana, siguiente semana, etc.), calcula las fechas apropiadas
6. Si el usuario menciona "esta semana", asume desde hoy hasta 6 días después
7. Si la pregunta no es sobre eventos, usa la herramienta chat
8. Responde siempre en {bot_language}
9. Sé amable y útil en tus respuestas
"""

    # ── General chat system prompt ───────────────────────────────────────────
    # Used when the AI falls through to a freeform chat response (tool="chat").
    chat_system: str = """\
Tu nombre es {bot_name}.
Eres un asistente personal amable y útil.
Responde siempre en {bot_language}.
"""


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL SINGLETON  ← EDIT THIS to change any prompt
# ═══════════════════════════════════════════════════════════════════════════

PROMPTS = PromptConfig(
    bot_name="LushJr",
    bot_language="The user's language",

    # Uncomment and edit any field below to override the default template.
    # Example:
    #   calendar_system="Eres un asistente minimalista. Solo responde con lo esencial.",
)


# ═══════════════════════════════════════════════════════════════════════════
# RENDER HELPERS
# These are called by providers / directives — you don't need to edit them.
# ═══════════════════════════════════════════════════════════════════════════

def render_intent_system(
    fecha_hoy: Optional[str] = None,
    dia_semana: Optional[str] = None,
) -> str:
    """Render the intent-detection system prompt with today's date context."""
    return PROMPTS.intent_system.format(
        bot_name=PROMPTS.bot_name,
        fecha_hoy=fecha_hoy or datetime.now().strftime("%Y-%m-%d"),
        dia_semana=dia_semana or datetime.now().strftime("%A"),
    )


def render_calendar_system() -> str:
    """Render the calendar directive system prompt."""
    return PROMPTS.calendar_system.format(
        bot_name=PROMPTS.bot_name,
        bot_language=PROMPTS.bot_language,
    )


def render_chat_system() -> str:
    """Render the general chat system prompt."""
    return PROMPTS.chat_system.format(
        bot_name=PROMPTS.bot_name,
        bot_language=PROMPTS.bot_language,
    )


def render_tool_selection_fallback(tool_descriptions: str, base_system: str) -> str:
    """
    Render the tool-selection fallback prompt.
    Appends tool list and JSON instruction to the base system prompt.
    """
    suffix = PROMPTS.tool_selection_fallback.format(
        tool_descriptions=tool_descriptions,
    )
    return base_system + suffix