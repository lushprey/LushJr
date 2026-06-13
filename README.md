# LushJr Bot

A modular, language-agnostic Telegram bot with AI and calendar management.
Swap any component — AI provider, calendar backend, or messaging platform — by changing one line in `config.yaml`.

---

## Project structure

```
LushJr_bot/
├── main.py                          # Composition root (wires everything together)
├── config.yaml                      # Plugin selection & settings
├── requirements.txt
│
├── core/
│   └── processor.py                 # MessageProcessor — orchestrates AI + tools
│
├── integrations/
│   ├── base.py                      # Abstract interfaces (Tool, Directive, AIProvider …)
│   │
│   ├── core_ai/                     # Plugin: Nvidia/OpenAI-compatible AI
│   │   ├── __init__.py              #   factory → create_ai_provider()
│   │   └── provider.py              #   NvidiaAIProvider
│   │
│   ├── calendar_notion/             # Plugin: Notion calendar
│   │   ├── __init__.py              #   factory → create_calendar_integration()
│   │   ├── integration.py           #   NotionCalendarIntegration
│   │   ├── directive.py             #   CalendarDirective (tools + system prompt)
│   │   └── tools.py                 #   QueryEventsTool, CreateEventTool, …
│   │
│   └── platform_telegram/           # Plugin: Telegram bot
│       ├── __init__.py              #   factory → create_platform_bot()
│       └── bot.py                   #   TelegramBot
│
├── agents/                          # Dev-time scripts (not used at runtime)
│   └── cache_agent.py               #   Cleans __pycache__ (VS Code only)
│
└── test_plugin_system.py            # Test suite (no API keys required)
```

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env with your credentials
cp .env.example .env   # then fill in the values

# 3. Run
python main.py
```

---

## Environment variables

```
TELEGRAM_TOKEN   — from @BotFather
NVIDIA_API_KEY   — from build.nvidia.com
NOTION_TOKEN     — Notion integration token
DATABASE_ID      — Notion database ID
```

---

## Swapping plugins

Edit `config.yaml`:

```yaml
plugins:
  ai:       core_ai            # swap to openai_plugin, anthropic_plugin, etc.
  calendar: calendar_notion    # swap to calendar_google, calendar_ical, etc.
  platform: platform_telegram  # swap to platform_discord, platform_whatsapp, etc.
```

No other file needs to change.

---

## Adding a new tool

1. Create a class in `integrations/calendar_notion/tools.py` that extends `Tool`.
2. Register it in `CalendarDirective.__init__()` in `directive.py`.

```python
class MyNewTool(Tool):
    name        = "my_tool"
    description = "Does something useful."
    params      = {
        "input": {"type": "string", "description": "The input", "required": True},
    }

    def execute(self, params) -> ToolResult:
        result = do_something(params["input"])
        return ToolResult(success=True, message=result)
```

---

## Adding a new plugin (e.g. Google Calendar)

1. Create `integrations/calendar_google/__init__.py` with a `create_calendar_integration()` factory.
2. Implement `CalendarIntegration` from `integrations/base.py`.
3. Set `calendar: calendar_google` in `config.yaml`.

---

## Chained actions

The AI can execute multiple tools in a single message.
For example, "delete all events this month" triggers several `delete_event` calls automatically — no extra code needed.

The flow:
```
user message
    ↓
AI.choose_tools()  →  [ToolCall, ToolCall, ToolCall, …]
    ↓
Execute each in sequence
    ↓
AI.chat(combined_results)  →  natural-language reply
```

---

## Running tests

```bash
python test_plugin_system.py
```

All 8 test sections run without API keys (uses mocks).

---

## Dependencies

```
python-telegram-bot==21.3
openai==1.42.0
httpx==0.27.2
notion-client==2.2.1
python-dotenv==1.0.0
```