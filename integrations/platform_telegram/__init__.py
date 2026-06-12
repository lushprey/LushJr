"""
integrations/platform_telegram/__init__.py
───────────────────────────────────────────
Factory for creating the Telegram platform plugin.
"""
import os

from core.processor import MessageProcessor
from .bot import TelegramBot


def create_platform_bot(processor: MessageProcessor = None) -> TelegramBot:
    """
    Factory function to create Telegram bot instance.
    Called by the plugin loader.
    
    Note: In the plugin loader, this will be called without arguments.
    The processor will be passed separately in main.py.
    
    Args:
        processor: MessageProcessor instance (optional, passed from main.py)
    
    Returns:
        TelegramBot instance
    """
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable not set")
    
    # If processor not provided, return a bot factory
    # The actual bot will be instantiated in main.py
    if processor is None:
        # Return a lambda that will be called with processor in main.py
        return lambda p: TelegramBot(token=token, processor=p)
    
    return TelegramBot(token=token, processor=processor)


__all__ = ["create_platform_bot", "TelegramBot"]
