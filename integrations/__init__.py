"""
integrations/__init__.py
────────────────────────
Plugin registry and loader for the modular bot system.
"""
import importlib
import os
from typing import Dict, Any, Tuple, Optional


# Plugin registry mapping: plugin_type -> default_plugin_name
DEFAULT_PLUGINS = {
    'calendar': 'calendar_notion',
    'ai': 'core_ai',
    'platform': 'platform_telegram',
}


# Import the new load_plugin and registry from the registry module
from .registry import load_plugin, registry, PluginRegistry


# Export the public names
__all__ = ["load_plugin", "DEFAULT_PLUGINS", "registry", "PluginRegistry"]