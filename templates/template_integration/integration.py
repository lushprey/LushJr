"""
integrations/template_integration/integration.py
───────────────────────────────────────────
Template integration implementation.

This template demonstrates how to create a custom integration by showing
how to inherit from BaseIntegration, the base class for all integration types.
To use this template:

1. Determine your plugin type (ai, calendar, platform, etc.)
2. Inherit from BaseIntegration and add any necessary functionality:
   - For AI providers: Add API client setup and implement AIProvider methods
   - For calendar integrations: Add calendar-specific logic and methods
   - For platform bots: Add platform-specific logic and implement PlatformBot methods
   - For other plugins: Add your specific integration logic
3. Implement the required methods for your chosen interface.
4. Adapt the __init__ method to handle your specific configuration needs.

The Base* classes in integrations.base provide common functionality.
"""

from integrations.base import BaseIntegration


class TemplateIntegration(BaseIntegration):
    """
    A template integration class showing how to inherit from a base integration class.

    EXAMPLE: This inherits from BaseIntegration, the base class for all integration types.

    To create a specific integration type, inherit from BaseIntegration and add the necessary functionality:

    - For AI providers: Add API client setup and implement AIProvider methods
    - For platform bots: Add platform-specific logic and implement PlatformBot methods
    - For other plugins: Add your specific integration logic

    The BaseIntegration class provides a common foundation for all integration types.
    """

    def __init__(self, token: str, api_base: str = None):
        """
        Initialize the template integration.

        Args:
            token: Authentication token for the service.
            api_base: Base URL for the API (if applicable).
        """
        # Initialize base integration
        super().__init__()

        # Store configuration (to be implemented by specific integrations)
        self.token = token
        self.api_base = api_base

    # ──────────────────────────────────────────────────────────────────────
    # EXAMPLE METHODS - IMPLEMENT BASED ON YOUR INTEGRATION TYPE
    # ──────────────────────────────────────────────────────────────────────

    # Implement the methods required for your specific integration type:
    # - AI providers: Implement AIProvider interface methods (chat, choose_tools)
    # - Calendar integrations: Implement CalendarIntegration interface methods
    #   (query_events, create_event, update_event, delete_event)
    # - Platform bots: Implement PlatformBot interface method (run)
    # - Other plugins: Implement your specific interface methods

    # EXAMPLE: A simple echo method for demonstration

    # EXAMPLE: A simple echo method for demonstration
    def echo(self, message: str) -> str:
        """
        Example method that echoes back a message.
        REPLACE THIS WITH YOUR ACTUAL INTEGRATION METHODS.
        """
        return f"Echo: {message}"


__all__ = ["TemplateIntegration"]