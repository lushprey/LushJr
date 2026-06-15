"""
integrations/template_calendar/__init__.py
───────────────────────────────────────────
Template for creating a custom calendar plugin.

To create a new calendar plugin:
1. Copy this directory to a new name (e.g., integrations/my_calendar).
2. Implement your calendar integration class in integration.py, inheriting from BaseCalendarIntegration.
3. Implement the four required methods: query_events, create_event, update_event, delete_event.
4. Create a directive class (or reuse CalendarDirective from the Notion plugin if suitable).
5. Update the factory function below to return an instance of your integration and directive.
6. Add any plugin-specific configuration to config.yaml under the 'calendar' section.
7. The bot will automatically discover and load the plugin via the registry.

Plugin type: calendar
"""
from .integration import TemplateCalendarIntegration
from .directive import TemplateCalendarDirective

# Plugin type identifier for auto-discovery
PLUGIN_TYPE = "calendar"


def create_calendar_integration(config: dict = None) -> tuple:
    """
    Factory function to create the template calendar integration and directive.

    Args:
        config: Configuration dictionary from config loader.

    Returns:
        Tuple of (CalendarIntegration, Directive)
    """
    # Extract configuration (example)
    # For this template, we expect configuration under config['calendar']
    # such as 'api_base', 'token_env', etc. Adjust as needed for your calendar.
    if config is None:
        import os
        # Fallback to environment variables for demonstration
        token = os.getenv("TEMPLATE_CALENDAR_TOKEN")
        database_id = os.getenv("TEMPLATE_CALENDAR_DATABASE_ID")
        if not token:
            raise ValueError("TEMPLATE_CALENDAR_TOKEN environment variable not set")
        if not database_id:
            raise ValueError("TEMPLATE_CALENDAR_DATABASE_ID environment variable not set")
    else:
        calendar_config = config.get("calendar", {})
        token = calendar_config.get("token") or os.getenv("TEMPLATE_CALENDAR_TOKEN")
        database_id = calendar_config.get("database_id") or os.getenv("TEMPLATE_CALENDAR_DATABASE_ID")
        if not token:
            raise ValueError("TEMPLATE_CALENDAR_TOKEN not found in config or environment variables")
        if not database_id:
            raise ValueError("TEMPLATE_CALENDAR_DATABASE_ID not found in config or environment variables")

    # Create integration
    integration = TemplateCalendarIntegration(
        token=token,
        database_id=database_id,
        # You can pass additional configuration here, e.g., api_base
        api_base=calendar_config.get("api_base") if config else None,
    )

    # Create directive
    directive = TemplateCalendarDirective(integration)

    return integration, directive


__all__ = [
    "create_calendar_integration",
    "TemplateCalendarIntegration",
    "TemplateCalendarDirective",
    "PLUGIN_TYPE",
]