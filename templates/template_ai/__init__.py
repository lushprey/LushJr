"""
integrations/template_ai/__init__.py
───────────────────────────────────────
Template for creating a custom AI provider plugin.

To create a new AI provider:
1. Copy this directory to a new name (e.g., integrations/my_ai).
2. Implement your AI provider class in provider.py, inheriting from BaseAIProvider.
3. Update the factory function below to return an instance of your class.
4. Add any plugin-specific configuration to config.yaml under the 'ai' section.
5. The bot will automatically discover and load the plugin via the registry.

Plugin type: ai
"""
from .provider import TemplateAIProvider

# Plugin type identifier for auto-discovery
PLUGIN_TYPE = "ai"


def create_ai_provider(config: dict = None) -> TemplateAIProvider:
    """
    Factory function to create the template AI provider.

    Args:
        config: Configuration dictionary from config loader.

    Returns:
        TemplateAIProvider instance.
    """
    # Extract configuration (example)
    api_key = None
    if config is not None:
        api_key = config.get("ai", {}).get("api_key") or config.get("ai", {}).get("api_key_env")
        # In practice, you would get the API key from environment variables or config
        # For this template, we expect the API key to be in the environment variable
        # specified by the config, or you can hardcode for demonstration (not recommended).
    if api_key is None:
        # Fallback to environment variable for demonstration
        import os
        api_key = os.getenv("TEMPLATE_AI_API_KEY")
        if not api_key:
            raise ValueError("API key not found for template AI provider")

    # For this template, we use fixed model and temperature; you can make these configurable
    return TemplateAIProvider(
        api_key=api_key,
        model="template/model",
        temperature=0.7,
    )


__all__ = ["create_ai_provider", "TemplateAIProvider", "PLUGIN_TYPE"]