"""
integrations/registry.py
────────────────────────
Plugin registry for auto-discovery and flexible loading.
"""
import importlib
import os
from typing import Dict, Any, Optional, Tuple

from . import DEFAULT_PLUGINS  # keep the default mapping for backward compatibility


class PluginRegistry:
    def __init__(self, integrations_path: str = None):
        """
        Initialize the registry by scanning the integrations directory.

        Args:
            integrations_path: Path to the integrations directory. Defaults to the directory containing this file.
        """
        if integrations_path is None:
            # Default to the directory containing this file
            self.integrations_path = os.path.join(os.path.dirname(__file__))
        else:
            self.integrations_path = integrations_path

        self._plugins: Dict[str, Dict[str, Any]] = {}  # plugin_type -> {plugin_name: module}
        self._discover_plugins()

    def _discover_plugins(self):
        """Scan the integrations directory for plugin modules."""
        try:
            items = os.listdir(self.integrations_path)
        except FileNotFoundError:
            return

        for item in items:
            plugin_dir = os.path.join(self.integrations_path, item)
            if not os.path.isdir(plugin_dir):
                continue

            # Check if it looks like a plugin (has __init__.py)
            init_file = os.path.join(plugin_dir, "__init__.py")
            if not os.path.isfile(init_file):
                continue

            try:
                # Import the module
                module_name = f"integrations.{item}"
                module = importlib.import_module(module_name)
            except Exception as e:
                # Log or skip; for now, we'll skip problematic modules
                continue

            # Check if the plugin declares its type
            plugin_type = getattr(module, "PLUGIN_TYPE", None)
            if plugin_type is None:
                # If not declared, we could try to infer from factories, but we'll skip for safety
                continue

            # Store the plugin
            if plugin_type not in self._plugins:
                self._plugins[plugin_type] = {}
            self._plugins[plugin_type][item] = module

    def get_plugin_types(self) -> Dict[str, list]:
        """Return discovered plugin types and their available plugin names."""
        result = {}
        for plugin_type, plugins in self._plugins.items():
            result[plugin_type] = list(plugins.keys())
        return result

    def load_plugin(
        self,
        plugin_type: str,
        plugin_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Load a plugin instance by type and name.

        Args:
            plugin_type: Type of plugin ('ai', 'calendar', 'platform')
            plugin_name: Name of specific plugin. If None, uses default from config or DEFAULT_PLUGINS.
            config: Configuration dictionary to pass to the factory function.

        Returns:
            Plugin instance (or tuple for calendar which returns (integration, directive)).

        Raises:
            ValueError: If plugin type is unknown or plugin not found.
            ImportError: If plugin module cannot be imported.
            AttributeError: If factory function is missing.
        """
        if plugin_type not in self._plugins:
            raise ValueError(f"Unknown plugin type: {plugin_type}. Available: {list(self._plugins.keys())}")

        plugins = self._plugins[plugin_type]

        # Determine which plugin to use
        if plugin_name is None:
            # Try to get from config overrides
            if config and "plugin_overrides" in config:
                plugin_name = config["plugin_overrides"].get(plugin_type)
            # Fallback to default plugins
            if plugin_name is None:
                plugin_name = DEFAULT_PLUGINS.get(plugin_type)
            # If still None, use the first discovered plugin as last resort
            if plugin_name is None and plugins:
                plugin_name = next(iter(plugins))

        if plugin_name is None:
            raise ValueError(
                f"No plugin specified for type {plugin_type} and no default available."
            )

        if plugin_name not in plugins:
            raise ValueError(
                f"Plugin '{plugin_name}' not found for type {plugin_type}. "
                f"Available: {list(plugins.keys())}"
            )

        module = plugins[plugin_name]

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

        # Call the factory with config if provided
        if config is not None:
            # We assume the factory now accepts an optional config argument
            # For backward compatibility, we'll try to call with config, and if it fails due to unexpected arg,
            # we'll call without config (but we will have updated factories by then).
            try:
                return factory(config=config)
            except TypeError as e:
                if "unexpected keyword argument" in str(e):
                    # Fallback for factories not yet updated
                    return factory()
                else:
                    raise
        else:
            return factory()


# Create a singleton registry instance for convenience
registry = PluginRegistry()


def load_plugin(plugin_type: str, plugin_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Any:
    """
    Load a plugin by type and name, using the global registry.
    This function maintains backward compatibility with the old load_plugin signature
    while adding config support.

    Args:
        plugin_type: Type of plugin ('calendar', 'ai', 'platform')
        plugin_name: Name of specific plugin. If None, uses default from config or DEFAULT_PLUGINS.
        config: Configuration dictionary to pass to the factory function.

    Returns:
        Plugin instance or tuple depending on plugin type.
    """
    return registry.load_plugin(plugin_type, plugin_name, config)


__all__ = ["load_plugin", "registry", "PluginRegistry"]