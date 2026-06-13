"""
main.py
────────
Composition root — the only place where concrete types are wired together.

To swap any component, change config.yaml (or DEFAULT_PLUGINS in
integrations/__init__.py).  Nothing else needs to change.
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

from core.processor import MessageProcessor
from integrations import load_plugin

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

    ai                          = load_plugin("ai")
    calendar, directive         = load_plugin("calendar")
    platform_factory            = load_plugin("platform")

    processor = MessageProcessor(ai=ai, directive=directive)

    bot = platform_factory(processor) if callable(platform_factory) else platform_factory
    logger.info("✅ All plugins loaded.")
    return bot


def main() -> None:
    _check_env()
    build_bot().run()


if __name__ == "__main__":
    main()