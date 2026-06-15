"""
integrations/platform_telegram/__init__.py
───────────────────────────────────────────
Factory for creating the Telegram platform plugin.
"""
from core.processor import MessageProcessor
from .bot import TelegramBot

# Plugin type identifier for auto-discovery
PLUGIN_TYPE = "platform"


def create_platform_bot(processor: MessageProcessor = None, config: dict = None) -> TelegramBot:
    """
    Factory function to create Telegram bot instance.

    Args:
        processor: MessageProcessor instance (optional, passed from main.py).
        config: Configuration dictionary from config loader. Must not None.

    Returns:
        TelegramBot instance
    """
    if config is None:
        raise ValueError("Config must be provided to platform plugin factory")

    # Extract platform configuration
    platform_config = config.get("platform", {})
    token = platform_config.get("token")
    if not token:
        raise ValueError("TELEGRAM_TOKEN not found in config under platform.token")

    # If processor not provided, return a bot factory
    # The actual bot will be instantiated in main.py
    if processor is None:
        # Return a lambda that will be called with processor in main.py
        return lambda p: TelegramBot(token=token, processor=p)

    return TelegramBot(token=token, processor=processor)


__all__ = ["create_platform_bot", "TelegramBot", "PLUGIN_TYPE"]