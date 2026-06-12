# LushJr_bot

_Auto-generated README - Last updated: 2026-06-12 09:57:42_

## Overview

Telegram bot with AI integration and calendar management.

## Project Structure

```
LushJr_bot/
├── core/
│   ├── __init__.py
│   ├── ai_provider.py
│   ├── data_integration.py
│   └── processor.py
├── integrations/
│   ├── __init__.py
│   ├── notion_calendar.py
│   └── nvidia_ai.py
├── main.py
├── platforms/
│   └── telegram_bot.py
├── README.md
├── readme_agent.py
└── requirements.txt
```

## Components

### Core

- **__init__.py**

- **ai_provider.py**

- **data_integration.py**

- **processor.py**


### Integrations

- **__init__.py**

- **notion_calendar.py**

- **nvidia_ai.py**


### Platforms

- **telegram_bot.py**


### Root

- **main.py**
 — main.py

- **readme_agent.py**
 — readme_agent.py


## Dependencies

```
python-telegram-bot==21.3
openai==1.42.0
httpx==0.27.2
notion-client==2.2.1
python-dotenv==1.0.0
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Configuration

Set up the following environment variables in a `.env` file:

- `TELEGRAM_TOKEN`
- `NVIDIA_API_KEY`
- `NOTION_TOKEN`
- `DATABASE_ID`
