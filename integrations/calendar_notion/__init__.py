"""
integrations/calendar_notion/__init__.py
─────────────────────────────────────────
Factory for creating the Notion calendar plugin.
This is a self-contained plugin that includes:
- Integration (NotionCalendarIntegration)
- Tools (query, create, update, delete)
- Directive (CalendarDirective)
"""
import os

from .integration import NotionCalendarIntegration
from .directive import CalendarDirective


def create_calendar_integration() -> tuple:
    """
    Factory function to create calendar integration and directive.
    Called by the plugin loader.
    
    Returns:
        Tuple of (CalendarIntegration, Directive)
    """
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("DATABASE_ID")
    
    if not notion_token:
        raise ValueError("NOTION_TOKEN environment variable not set")
    if not database_id:
        raise ValueError("DATABASE_ID environment variable not set")
    
    # Create integration
    integration = NotionCalendarIntegration(
        token=notion_token,
        database_id=database_id,
    )
    
    # Create directive with the integration
    directive = CalendarDirective(integration)
    
    return integration, directive


__all__ = [
    "create_calendar_integration",
    "NotionCalendarIntegration",
    "CalendarDirective",
]
