"""
integrations/core_ai/__init__.py
─────────────────────────────────
Factory for creating the AI provider plugin.
"""

from .provider import NvidiaAIProvider

# Plugin type identifier for auto-discovery
PLUGIN_TYPE = "ai"


def create_ai_provider(config: dict) -> NvidiaAIProvider:
    """
    Factory function to create AI provider.

    Args:
        config: Configuration dictionary from config loader.

    Returns:
        NvidiaAIProvider instance.
    """
    # Extract AI configuration
    ai_config = config.get("ai", {})
    api_key = ai_config.get("api_key")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY not found in config under ai.api_key")

    model = ai_config.get("model", "meta/llama-3.3-70b-instruct")
    temperature = ai_config.get("temperature", 0.7)
    api_base = ai_config.get("api_base")  # None means use default in provider

    return NvidiaAIProvider(
        api_key=api_key,
        model=model,
        temperature=temperature,
        api_base=api_base,
    )


__all__ = ["create_ai_provider", "NvidiaAIProvider", "PLUGIN_TYPE"]