"""
main.py
────────
Composition root — the only place where concrete types are wired together.

To swap any component, change config.yaml (or plugin overrides in config.yaml).
Nothing else needs to change.
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

from core.processor import MessageProcessor
from integrations import load_plugin
from config.loader import load_config

load_dotenv()

logging.basicConfig(
    format="%(asctime)s │ %(levelname)s │ %(name)s │ %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

_REQUIRED_ENV = ["TELEGRAM_TOKEN", "NVIDIA_API_KEY", "NOTION_TOKEN", "DATABASE_ID"]


def _check_env() -> None:
    missing = [v for v in _REQUIRED_ENV if not os.getenv(v)]
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")


def build_bot():
    logger.info("🔌 Loading plugins…")

    # Load configuration (non-secret settings from config.yaml, secrets from env via loader)
    config = load_config()

    # Ensure required environment variables are present (for secrets)
    _check_env()

    # Load plugins using the registry, passing config to factories
    ai = load_plugin("ai", config=config)
    assistant_integration, directive = load_plugin("calendar", config=config)
    platform_factory = load_plugin("platform", config=config)

    processor = MessageProcessor(ai=ai, directive=directive)

    bot = platform_factory(processor) if callable(platform_factory) else platform_factory
    logger.info("✅ All plugins loaded.")
    return bot


def main() -> None:
    _check_env()
    build_bot().run()


if __name__ == "__main__":
    main()