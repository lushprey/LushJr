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


def load_plugin(plugin_type: str, plugin_name: Optional[str] = None) -> Any:
    """
    Load a plugin by type and name.
    
    Args:
        plugin_type: Type of plugin ('calendar', 'ai', 'platform')
        plugin_name: Name of specific plugin. If None, uses default from DEFAULT_PLUGINS
        
    Returns:
        Plugin instance or tuple depending on plugin type
        
    Raises:
        ImportError: If plugin cannot be loaded
        AttributeError: If plugin doesn't have factory function
    """
    if plugin_name is None:
        plugin_name = DEFAULT_PLUGINS.get(plugin_type)
        if plugin_name is None:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
    
    # Construct module path: integrations.{plugin_name}
    module_path = f"integrations.{plugin_name}"
    
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise ImportError(f"Plugin module not found: {module_path}")
    
    # Get factory function based on plugin type
    factory_names = {
        'calendar': 'create_calendar_integration',
        'ai': 'create_ai_provider',
        'platform': 'create_platform_bot',
    }
    
    factory_name = factory_names.get(plugin_type)
    if factory_name is None:
        raise ValueError(f"Unknown plugin type: {plugin_type}")
    
    if not hasattr(module, factory_name):
        raise AttributeError(
            f"Plugin {plugin_name} doesn't have {factory_name}() factory function"
        )
    
    factory = getattr(module, factory_name)
    return factory()


__all__ = ["load_plugin", "DEFAULT_PLUGINS"]
