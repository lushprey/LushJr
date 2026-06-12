"""
integrations/core_ai/__init__.py
─────────────────────────────────
Factory for creating the AI provider plugin.
"""
import os

from .provider import NvidiaAIProvider


def create_ai_provider():
    """
    Factory function to create AI provider.
    Called by the plugin loader.
    """
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY environment variable not set")
    
    return NvidiaAIProvider(api_key=api_key)


__all__ = ["create_ai_provider", "NvidiaAIProvider"]
