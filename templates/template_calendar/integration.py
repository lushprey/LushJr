"""
integrations/template_calendar/integration.py
───────────────────────────────────────────
Template calendar integration implementation.

This template demonstrates how to create a custom calendar integration by
inheriting from BaseCalendarIntegration (defined in integrations.base).
BaseCalendarIntegration provides an HTTP client setup (similar to the
Notion integration) but leaves the four calendar methods abstract.

You must implement:
- query_events
- create_event
- update_event
- delete_event

If your calendar API is not HTTP-based, you may choose not to use
BaseCalendarIntegration and instead implement CalendarIntegration directly.
"""

from integrations.base import BaseCalendarIntegration, CalendarEvent


class TemplateCalendarIntegration(BaseCalendarIntegration):
    """
    A template calendar integration that inherits from BaseCalendarIntegration.

    BaseCalendarIntegration provides:
    - An httpx client configured with a bearer token and base URL.
    - Abstract methods for the four calendar operations.

    To use a different authentication method or API structure, you may
    need to override the __init__ method and not call super().__init__.
    """

    def __init__(self, token: str, database_id: str, api_base: str = None):
        """
        Initialize the template calendar integration.

        Args:
            token: Authentication token for the calendar service.
            database_id: Identifier for the calendar or database to interact with.
            api_base: Base URL for the calendar API. If None, uses a default
                      (you should set this to your API's base URL).
        """
        # If you want to use the BaseCalendarIntegration's HTTP client,
        # call super().__init__ with the token and api_base.
        # For demonstration, we'll just store the parameters.
        self.token = token
        self.database_id = database_id
        self.api_base = api_base
        # TODO: Set up your actual client here (e.g., service-specific client)
        # For now, we leave the client as None and the methods will raise if called.

    # ──────────────────────────────────────────────────────────────────────
    # CalendarIntegration interface (implement these)
    # ──────────────────────────────────────────────────────────────────────

    def query_events(self, date_start: str, date_end: str) -> list[CalendarEvent]:
        """
        Return events whose start date falls in [date_start, date_end].

        Args:
            date_start: Start date in ISO-8601 format (YYYY-MM-DD).
            date_end: End date in ISO-8601 format (YYYY-MM-DD).

        Returns:
            List of CalendarEvent objects.
        """
        # TODO: Implement actual query to your calendar service.
        # For now, return an empty list.
        return []

    def create_event(
        self,
        title: str,
        date_start: str,
        date_end: str | None = None,
        time_start: str | None = None,
        time_end: str | None = None,
        location: str | None = None,
        description: str | None = None,
    ) -> CalendarEvent:
        """
        Create a new calendar event.

        Args:
            title: Event title.
            date_start: Start date (YYYY-MM-DD).
            date_end: End date (YYYY-MM-DD) or None.
            time_start: Start time (HH:MM) or None.
            time_end: End time (HH:MM) or None.
            location: Event location or None.
            description: Event description or None.

        Returns:
            The created CalendarEvent.
        """
        # TODO: Implement actual event creation.
        # For now, return a dummy event.
        import uuid
        return CalendarEvent(
            id=str(uuid.uuid4()),
            title=title,
            date_start=date_start,
            date_end=date_end,
            time_start=time_start,
            time_end=time_end,
            location=location,
            description=description,
        )

    def update_event(
        self,
        event_id: str,
        title: str | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
        time_start: str | None = None,
        time_end: str | None = None,
        location: str | None = None,
        description: str | None = None,
    ) -> CalendarEvent:
        """
        Update an existing calendar event.

        Args:
            event_id: ID of the event to update.
            title: New title or None.
            date_start: New start date or None.
            date_end: New end date or None.
            time_start: New start time or None.
            time_end: New end time or None.
            location: New location or None.
            description: New description or None.

        Returns:
            The updated CalendarEvent.
        """
        # TODO: Implement actual event update.
        # For now, return a dummy event with the given ID.
        return CalendarEvent(
            id=event_id,
            title=title or "Untitled",
            date_start=date_start or "1970-01-01",
            date_end=date_end,
            time_start=time_start,
            time_end=time_end,
            location=location,
            description=description,
        )

    def delete_event(self, event_id: str) -> None:
        """
        Delete a calendar event.

        Args:
            event_id: ID of the event to delete.
        """
        # TODO: Implement actual event deletion.
        pass


__all__ = ["TemplateCalendarIntegration"]