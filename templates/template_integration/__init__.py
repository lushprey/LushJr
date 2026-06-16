"""
integrations/my_data/__init__.py
─────────────────────────────────
Factory for the custom data integration plugin.

This module auto-discovers the plugin and creates instances.

To use:
1. Copy to integrations/my_data/
2. Update PLUGIN_TYPE if not "calendar" (could be "tasks", "notes", etc)
3. Implement create_calendar_integration() or create_[type]_integration()
4. Update config.yaml with your plugin's configuration section
"""

from .integration import MyDataIntegration
from .directive import MyDataDirective

# Plugin type identifier (used by registry for auto-discovery)
PLUGIN_TYPE = "calendar"  # Change to your actual type if different


def create_calendar_integration(config: dict = None) -> tuple:
    """
    Factory function to create data integration and directive.

    The registry will call this with the full config dictionary.
    Return a tuple of (integration, directive).

    Args:
        config: Full configuration dictionary from config.yaml
                Expected keys:
                - calendar.api_base (optional)
                - calendar.database_id (optional)
                - calendar.token (from environment variable)
                - system_prompts.default (optional, for base prompt)

    Returns:
        Tuple of (MyDataIntegration, MyDataDirective)

    Raises:
        ValueError: If required configuration is missing
    """
    if config is None:
        raise ValueError("Config dictionary is required for data integration factory")

    # Extract data integration configuration
    data_config = config.get("calendar", {})  # or your config section name

    # Get token (usually required)
    token = data_config.get("token")
    if not token:
        raise ValueError(
            "Authentication token not found in config['calendar']['token']. "
            "Ensure your config.yaml has:\n"
            "  calendar:\n"
            "    token_env: MY_DATA_TOKEN\n"
            "And .env has: MY_DATA_TOKEN=your_actual_token"
        )

    # Get other optional parameters
    api_base = data_config.get("api_base")
    database_id = data_config.get("database_id")

    # Create integration
    integration = MyDataIntegration(
        token=token,
        api_base=api_base,
        database_id=database_id,
    )

    # Get base system prompt from config (if available)
    base_system_prompt = None
    if config:
        system_prompts_config = config.get("system_prompts", {})
        base_system_prompt = system_prompts_config.get("default")

    # Create directive with integration and optional system prompt
    directive = MyDataDirective(
        integration=integration,
        system_prompt=base_system_prompt,
    )

    return integration, directive


__all__ = [
    "create_calendar_integration",
    "MyDataIntegration",
    "MyDataDirective",
    "PLUGIN_TYPE",
]