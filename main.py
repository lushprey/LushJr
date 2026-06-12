"""
Bot de Telegram con IA + Calendario Notion — Lenguaje Natural
=============================================================
Sin comandos. El bot entiende lenguaje natural:
  "¿qué tengo mañana?"         → consulta Notion
  "agenda una reunión el viernes" → crea evento en Notion
  "¿cómo me organizo mejor?"   → responde con IA
"""

import asyncio
import json
import os
import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from openai import OpenAI
from notion_client import Client
from dotenv import load_dotenv

# ─── Setup ───────────────────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    format="%(asctime)s │ %(levelname)s │ %(name)s │ %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NOTION_TOKEN   = os.getenv("NOTION_TOKEN")
DATABASE_ID    = os.getenv("DATABASE_ID")

PROP_TITULO = "Nombre"
PROP_FECHA  = "Fecha"

NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"

# ─── Clientes ─────────────────────────────────────────────────────────────────

ai     = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
notion = Client(auth=NOTION_TOKEN)

# ─── Herramientas de Notion ───────────────────────────────────────────────────

def _titulo(item: dict) -> str:
    partes = item["properties"].get(PROP_TITULO, {}).get("title", [])
    return partes[0]["plain_text"] if partes else "(sin título)"

def _fecha_str(item: dict) -> str:
    fecha = item["properties"].get(PROP_FECHA, {}).get("date")
    return fecha["start"] if fecha else "Sin fecha"

def consultar_eventos(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "and": [
                {"property": PROP_FECHA, "date": {"on_or_after":  fecha_inicio}},
                {"property": PROP_FECHA, "date": {"on_or_before": fecha_fin}},
            ]
        },
        sorts=[{"property": PROP_FECHA, "direction": "ascending"}],
    )
    return response.get("results", [])

def crear_evento(titulo: str, fecha: str) -> None:
    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            PROP_TITULO: {"title": [{"text": {"content": titulo}}]},
            PROP_FECHA:  {"date":  {"start": fecha}},
        },
    )

# ─── Motor de intención con IA ────────────────────────────────────────────────

HOY = lambda: datetime.now().strftime("%Y-%m-%d")

SYSTEM_INTENT = f"""\
Tu nombre es LushJr.
Eres el cerebro de un asistente personal en Telegram conectado a un calendario Notion cuyo modelo es Llama 3.1.
Hoy es {HOY()} ({datetime.now().strftime("%A")}).

Tu única tarea es analizar el mensaje del usuario y devolver un JSON con esta estructura exacta:

{{
  "accion": "consultar" | "crear" | "chat",
  "fecha_inicio": "YYYY-MM-DD",   // solo si accion es "consultar" o "crear"
  "fecha_fin": "YYYY-MM-DD",      // solo si accion es "consultar"
  "titulo": "texto del evento",   // solo si accion es "crear"
  "respuesta_directa": "texto"    // solo si accion es "chat"
}}

Reglas:
- "consultar": el usuario pregunta por eventos (hoy, mañana, esta semana, una fecha, etc.)
- "crear": el usuario quiere agendar/agregar/crear un evento
- "chat": cualquier otra pregunta o conversación
- Para fechas relativas usa la fecha de hoy como referencia
- Para "esta semana" usa fecha_fin = hoy + 6 días
- SOLO devuelve el JSON, sin explicaciones ni markdown
"""

def decidir_accion(mensaje: str) -> dict:
    """Llama a la IA para interpretar la intención del mensaje."""
    completion = ai.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_INTENT},
            {"role": "user",   "content": mensaje},
        ],
        temperature=0.5,   # Determinista para el parsing
        max_tokens=200,
    )
    raw = completion.choices[0].message.content.strip()
    # Limpiar posibles backticks que el modelo añada
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


SYSTEM_RESPUESTA = """\
Eres un asistente personal amigable integrado en Telegram.
Tu modelo es Llama 3.1.
Tu nombre es LushJr.
Responde de forma natural, fluida y en español.
Usa emojis con moderación.
"""

def generar_respuesta_chat(mensaje: str) -> str:
    """Respuesta libre de IA para mensajes que no son del calendario."""
    completion = ai.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_RESPUESTA},
            {"role": "user",   "content": mensaje},
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return completion.choices[0].message.content.strip()

# ─── Lógica principal ─────────────────────────────────────────────────────────

def procesar_mensaje(mensaje: str) -> str:
    """
    Pipeline completo:
    1. Interpreta intención con IA
    2. Ejecuta la acción correspondiente en Notion o responde con IA
    3. Devuelve texto listo para enviar a Telegram
    """
    try:
        intencion = decidir_accion(mensaje)
        logger.info(f"Intención detectada: {intencion}")
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"No se pudo parsear intención, fallback a chat: {e}")
        return generar_respuesta_chat(mensaje)

    accion = intencion.get("accion", "chat")

    # ── Consultar eventos ────────────────────────────────────────────────────
    if accion == "consultar":
        fecha_inicio = intencion.get("fecha_inicio", HOY())
        fecha_fin    = intencion.get("fecha_fin", fecha_inicio)
        try:
            items = consultar_eventos(fecha_inicio, fecha_fin)
        except Exception as e:
            logger.exception("Error consultando Notion")
            return f"❌ No pude consultar el calendario: {e}"

        if not items:
            if fecha_inicio == fecha_fin:
                return f"📭 No tienes eventos el {fecha_inicio}."
            return f"📭 No tienes eventos entre {fecha_inicio} y {fecha_fin}."

        if fecha_inicio == fecha_fin:
            encabezado = f"📅 Eventos del {fecha_inicio}:"
        else:
            encabezado = f"📆 Eventos del {fecha_inicio} al {fecha_fin}:"

        lineas = [f"• {_fecha_str(i)} — {_titulo(i)}" for i in items]
        return encabezado + "\n\n" + "\n".join(lineas)

    # ── Crear evento ─────────────────────────────────────────────────────────
    elif accion == "crear":
        titulo = intencion.get("titulo", "").strip()
        fecha  = intencion.get("fecha_inicio", HOY())

        if not titulo:
            return "⚠️ No entendí el nombre del evento. ¿Puedes repetirlo con más detalle?"

        try:
            crear_evento(titulo, fecha)
        except Exception as e:
            logger.exception("Error creando evento en Notion")
            return f"❌ No pude crear el evento: {e}"

        return f"✅ Listo, agendé *{titulo}* para el {fecha} 📌"

    # ── Chat libre ───────────────────────────────────────────────────────────
    else:
        respuesta_directa = intencion.get("respuesta_directa", "").strip()
        if respuesta_directa:
            return respuesta_directa
        return generar_respuesta_chat(mensaje)


# ─── Handler de Telegram ─────────────────────────────────────────────────────

async def on_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = update.message.text
    user  = update.effective_user.first_name if update.effective_user else "?"
    logger.info(f"[{user}] {texto!r}")

    try:
        await update.message.chat.send_action("typing")
    except Exception as e:
        logger.warning(f"No se pudo enviar typing: {e}")

    loop = asyncio.get_event_loop()
    try:
        respuesta = await loop.run_in_executor(None, procesar_mensaje, texto)
    except Exception as e:
        logger.exception("Error inesperado en procesar_mensaje")
        respuesta = f"❌ Algo salió mal: {e}"

    # Telegram: máx 4096 chars por mensaje
    for i in range(0, len(respuesta), 4096):
        await update.message.reply_text(
            respuesta[i : i + 4096],
            parse_mode="Markdown",
        )


# ─── Punto de entrada ─────────────────────────────────────────────────────────

def main() -> None:
    missing = [v for v in ["TELEGRAM_TOKEN","NVIDIA_API_KEY","NOTION_TOKEN","DATABASE_ID"]
               if not os.getenv(v)]
    if missing:
        raise EnvironmentError(f"Faltan variables de entorno: {', '.join(missing)}")

    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30,
        read_timeout=90,   # La llamada doble de IA puede tardar
        write_timeout=30,
        pool_timeout=30,
    )

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .request(request)
        .build()
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_mensaje))

    logger.info("🤖 Bot iniciado — modo lenguaje natural")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        bootstrap_retries=5,
    )


if __name__ == "__main__":
    main()