# LushJr Bot

A modular, language-agnostic Telegram bot with AI and Notion integration.

The project uses a plugin architecture that allows components to be replaced independently (AI provider, Notion backend, messaging platform) without modifying the core logic.

---

## Project structure

```
LushJr_bot/
├── main.py                          # Composition root (wires everything together)
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
│   ├── calendar_notion/             # Plugin: Notion integration
│   │   ├── __init__.py              #   factory → create_calendar_integration()
│   │   ├── integration.py           #   NotionCalendarIntegration
│   │   ├── directive.py             #   CalendarDirective (tools + system prompt)
│   │   └── tools.py                 #   QueryEventsTool, CreateEventTool, …
│   │
│   └── platform_telegram/           # Plugin: Telegram bot
│       ├── __init__.py              #   factory → create_platform_bot()
│       └── bot.py                   #   TelegramBot
│
├── agents/                          # Development utilities
│
└── test_plugin_system.py            # Test suite (no API keys required)
```

---

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env with your credentials
cp .env.example .env

# Run the bot
python main.py
```

---

## Environment variables

```
TELEGRAM_TOKEN   — Telegram bot token from @BotFather
NVIDIA_API_KEY   — NVIDIA API key
NOTION_TOKEN     — Notion integration token
DATABASE_ID      — Notion database ID
```

---

## Plugin architecture

LushJr separates its responsibilities into independent modules:

- **Core** → orchestration logic.
- **AI provider** → language model integration.
- **Calendar integration** → event management backend.
- **Platform integration** → communication channel.

The core never depends directly on a specific implementation.

---

## Adding a new tool

1. Create a class extending `Tool`.
2. Implement the required metadata and `execute()` method.
3. Register the tool inside the corresponding directive.

Example:

```python
class MyNewTool(Tool):
    name = "my_tool"
    description = "Does something useful."
    params = {
        "input": {
            "type": "string",
            "description": "The input",
            "required": True,
        }
    }

    def execute(self, params):
        result = do_something(params["input"])

        return ToolResult(
            success=True,
            message=result,
        )
```

---

## Adding a new plugin (Beginner-friendly)

We provide template directories for each plugin type to minimize boilerplate.
To create a new plugin, copy the appropriate template and implement the required logic.

### Using the Templates

1. **Choose a template** based on the plugin type you want to create:
   - `integrations/template_ai` for a new AI provider
   - `integrations/template_calendar` for a new integration (adaptable to any plugin type)
   - `integrations/template_platform` for a new messaging platform

2. **Copy the template** to a new directory with your plugin's name:
   ```bash
   # Example: creating a new AI provider called "my_ai"
   cp -r integrations/template_ai integrations/my_ai
   ```

3. **Implement your plugin**:
   - Edit the files in the new directory (see the docstrings in each file for guidance).
   - For AI provider: modify `provider.py` to implement actual AI logic.
   - For calendar: modify `integration.py` to implement the calendar methods.
   - For platform: modify `bot.py` to implement the `run` method with your platform's logic.
   - Update `__init__.py` as needed (especially the factory function to handle your configuration).

4. **Configure your plugin**:
   - Add any required configuration to `config.yaml` under the appropriate section (`ai`, `calendar`, or `platform`).
   - For secrets (API keys, tokens), the configuration loader reads them from environment variables (as specified in `config.yaml` using `_env` fields).
   - Example: to set a custom model for your AI provider, add under `ai`:
     ```yaml
     model: "your-model-name"
     ```

5. **The bot will automatically discover and load your plugin** via the plugin registry in `integrations/registry.py`.
   - If you want to explicitly specify which plugin to use (e.g., to override the default), you can add plugin overrides in `config.yaml`:
     ```yaml
     plugin_overrides:
       ai: "my_ai"
       calendar: "my_calendar"
       platform: "my_platform"
     ```

### Examples of Plugins You Can Create

- **AI providers**: OpenAI, Anthropic, Hugging Face, local LLMs (llama.cpp, etc.)
- **Data & service integrations**: Google Calendar, Outlook, iCal, databases, APIs, etc.
- **Platform integrations**: Discord, Slack, WhatsApp, web UI, etc.

---

## Note on Backward Compatibility

Backward compatibility has been removed for simplicity. All plugins now require a configuration dictionary (provided by the config loader) and no longer fall back to reading environment variables directly. The config loader itself reads secrets from environment variables (as specified in `config.yaml`), so you continue to set `TELEGRAM_TOKEN`, `NVIDIA_API_KEY`, `NOTION_TOKEN`, and `DATABASE_ID` in your `.env` file.

---

## Chained actions

The AI can execute multiple tools during a single interaction.

Example:

```
"Delete all events this month."
```

may generate several consecutive tool calls automatically.

Flow:

```
User message
    ↓
AI.choose_tools()
    ↓
[ToolCall, ToolCall, ToolCall]
    ↓
Execute tools sequentially
    ↓
AI.chat(results)
    ↓
Natural-language response
```

---

## Running tests

```bash
python test_plugin_system.py
```

The tests run without external API keys by using mocks.

---

## Dependencies

```
python-telegram-bot==21.3
openai==1.42.0
httpx==0.27.2
notion-client==2.2.1
python-dotenv==1.0.0
```