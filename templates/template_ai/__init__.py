"""
integrations/my_ai/__init__.py
──────────────────────────────
Factory for the custom AI provider plugin.

This module auto-discovers the plugin via PLUGIN_TYPE and creates
instances through the factory function.

To use:
1. Copy to integrations/my_ai/
2. Update PLUGIN_TYPE if not "ai"
3. Implement create_ai_provider() factory
4. Update config.yaml with your plugin's configuration section
"""

from .provider import MyAIProvider

# Plugin type identifier (used by registry for auto-discovery)
PLUGIN_TYPE = "ai"


def create_ai_provider(config: dict = None) -> MyAIProvider:
    """
    Factory function to create the AI provider instance.

    The registry will call this with the full config dictionary.
    Extract the configuration you need and return your provider.

    Args:
        config: Full configuration dictionary from config.yaml
                Keys you might need:
                - ai.api_key (or from environment variable)
                - ai.model
                - ai.temperature
                - ai.api_base (optional)

    Returns:
        MyAIProvider instance

    Raises:
        ValueError: If required configuration is missing
    """
    if config is None:
        raise ValueError("Config dictionary is required for AI provider factory")

    # Extract AI-specific configuration
    ai_config = config.get("ai", {})

    # Get API key (required)
    api_key = ai_config.get("api_key")
    if not api_key:
        raise ValueError(
            "API key not found in config['ai']['api_key']. "
            "Ensure your config.yaml has:\n"
            "  ai:\n"
            "    api_key_env: MY_AI_API_KEY\n"
            "And .env has: MY_AI_API_KEY=your_actual_key"
        )

    # Get model (with default fallback)
    model = ai_config.get("model", "default-model")

    # Get other optional parameters
    temperature = ai_config.get("temperature", 0.7)
    api_base = ai_config.get("api_base")

    # Create and return the provider instance
    return MyAIProvider(
        api_key=api_key,
        model=model,
        temperature=temperature,
        api_base=api_base,
    )


__all__ = ["create_ai_provider", "MyAIProvider", "PLUGIN_TYPE"]