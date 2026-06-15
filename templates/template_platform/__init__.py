"""
integrations/template_platform/__init__.py
───────────────────────────────────────────
Template for creating a custom platform plugin.

To create a new platform plugin:
1. Copy this directory to a new name (e.g., integrations/my_platform).
2. Implement your platform bot class in bot.py, inheriting from BasePlatformBot.
3. Implement the run method to start your platform's messaging loop.
4. Update the factory function below to return an instance of your class.
5. Add any plugin-specific configuration to config.yaml under the 'platform' section.
6. The bot will automatically discover and load the plugin via the registry.

Plugin type: platform
"""
from .bot import TemplatePlatformBot

# Plugin type identifier for auto-discovery
PLUGIN_TYPE = "platform"


def create_platform_bot(processor: "MessageProcessor" = None, config: dict = None) -> TemplatePlatformBot:
    """
    Factory function to create the template platform bot.

    Args:
        processor: MessageProcessor instance (optional, passed from main.py).
        config: Configuration dictionary from config loader.

    Returns:
        TemplatePlatformBot instance.
    """
    # Extract configuration (example)
    token = None
    if config is not None:
        token = config.get("platform", {}).get("token") or config.get("platform", {}).get("token_env")
        # In practice, you would get the token from environment variables or config
    if token is None:
        # Fallback to environment variable for demonstration
        import os
        token = os.getenv("TEMPLATE_PLATFORM_TOKEN")
        if not token:
            raise ValueError("Token not found for template platform plugin")

    # For this template, we assume the token is the only required config
    return TemplatePlatformBot(
        token=token,
        processor=processor,
    )


__all__ = ["create_platform_bot", "TemplatePlatformBot", "PLUGIN_TYPE"]