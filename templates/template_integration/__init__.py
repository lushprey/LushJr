"""
integrations/template_calendar/__init__.py
───────────────────────────────────────────
Template for creating a custom integration plugin.

This template demonstrates the basic structure for creating any type of integration
plugin (AI provider, calendar integration, platform bot, etc.). To adapt this template
for your specific integration type:

1. Copy this directory to a new name (e.g., integrations/my_integration).
2. Determine your plugin type (ai, calendar, platform, or custom):
   - For AI providers: implement AIProvider interface
   - For calendar integrations: implement CalendarIntegration interface
   - For platform bots: implement PlatformBot interface
   - For other integrations: implement the appropriate interface
3. Update the factory function name and PLUGIN_TYPE below to match your plugin type.
4. Implement your integration class in integration.py, inheriting from the appropriate base class.
5. Create tools and a directive as needed for your integration.
6. Add any plugin-specific configuration to config.yaml under your plugin's section.
7. The bot will automatically discover and load the plugin via the registry.

To use this template for a specific plugin type, change:
- PLUGIN_TYPE: set to your plugin type ('ai', 'calendar', 'platform', etc.)
- Factory function name: match the expected factory for your type:
   * ai: create_ai_provider
   * calendar: create_calendar_integration
   * platform: create_platform_bot
   * other: choose an appropriate name
"""
from .integration import TemplateIntegration
from .directive import TemplateDirective

# Plugin type identifier for auto-discovery
# CHANGE THIS TO MATCH YOUR PLUGIN TYPE (e.g., 'ai', 'calendar', 'platform')
PLUGIN_TYPE = "integration"  # Placeholder - change to your actual plugin type


def create_integration(config: dict = None):
    """
    Factory function to create the template integration.
    CHANGE THIS FUNCTION NAME TO MATCH YOUR PLUGIN TYPE:
    - AI providers: create_ai_provider
    - Calendar integrations: create_calendar_integration
    - Platform bots: create_platform_bot

    Args:
        config: Configuration dictionary from config loader.

    Returns:
        Plugin instance (type depends on your plugin type).
    """
    # Extract configuration (example)
    # Adapt this section based on your plugin's configuration needs
    if config is None:
        import os
        # Example fallback to environment variables
        token = os.getenv("TEMPLATE_INTEGRATION_TOKEN")
        if not token:
            raise ValueError("TEMPLATE_INTEGRATION_TOKEN environment variable not set")
    else:
        # Get config for your plugin type (adjust the key as needed)
        plugin_config = config.get("integration", {})  # CHANGE 'integration' to your config key
        token = plugin_config.get("token") or os.getenv("TEMPLATE_INTEGRATION_TOKEN")
        if not token:
            raise ValueError("TEMPLATE_INTEGRATION_TOKEN not found in config or environment variables")

    # Create integration
    # CHANGE THIS TO USE YOUR ACTUAL INTEGRATION CLASS
    integration = TemplateIntegration(
        token=token,
        # Add other parameters as needed for your integration
    )

    # Create directive (if applicable to your plugin type)
    # Some plugin types (like AI providers) don't use directives
    directive = TemplateDirective(integration) if integration else None

    return integration, directive


__all__ = [
    "create_integration",
    "TemplateIntegration",
    "TemplateDirective",
    "PLUGIN_TYPE",
]