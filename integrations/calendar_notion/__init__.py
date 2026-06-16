"""
integrations/calendar_notion/__init__.py
─────────────────────────────────────────
Factory for creating the Notion calendar plugin.
This is a self-contained plugin that includes:
- Integration (NotionCalendarIntegration)
- Tools (query, create, update, delete)
- Directive (CalendarDirective)
"""

from .integration import NotionCalendarIntegration
from .directive import CalendarDirective

# Plugin type identifier for auto-discovery
PLUGIN_TYPE = "calendar"


def create_calendar_integration(config: dict) -> tuple:
    """
    Factory function to create calendar integration and directive.

    Args:
        config: Configuration dictionary from config loader.

    Returns:
        Tuple of (CalendarIntegration, Directive)
    """
    # Extract calendar configuration
    calendar_config = config.get("calendar", {})
    notion_token = calendar_config.get("token")
    database_id = calendar_config.get("database_id")

    if not notion_token:
        raise ValueError("NOTION_TOKEN not found in config under calendar.token")
    if not database_id:
        raise ValueError("DATABASE_ID not found in config under calendar.database_id")

    # Create integration
    integration = NotionCalendarIntegration(
        token=notion_token,
        database_id=database_id,
    )

    # Extract system prompt from config if available
    system_prompt = None
    if config is not None:
        system_prompts_config = config.get("system_prompts", {})
        system_prompt = system_prompts_config.get("default")

    # Create directive with the integration and optional system prompt
    directive = CalendarDirective(integration, system_prompt=system_prompt)

    return integration, directive


__all__ = [
    "create_calendar_integration",
    "NotionCalendarIntegration",
    "CalendarDirective",
    "PLUGIN_TYPE",
]