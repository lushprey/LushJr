"""
integrations/template_calendar/directive.py
───────────────────────────────────────────
Template directive implementation.

This template demonstrates how to create a directive for your integration.
A directive bundles tools and a system prompt, and is primarily used with
certain plugin types (like calendar integrations).

Not all plugin types use directives:
- AI providers: Typically don't use directives (handle prompting directly)
- Platform bots: May or may not use directives depending on design
- Other integrations: Use directives as needed for your architecture

If your plugin type uses directives, you can:
- Create your own directive as shown below, wrapping your integration's methods with tools
- Reuse existing directives if they match your tool interfaces
- Adapt the pattern to your specific needs

For simplicity, this template creates a directive with basic example tools
that demonstrate the tool creation pattern.
"""

from integrations.base import BaseDirective, Directive, Tool, ToolResult


class ExampleQueryTool(Tool):
    """Example tool demonstrating the tool pattern."""
    def __init__(self, integration):
        self._integration = integration

    @property
    def name(self) -> str:
        return "example_query"

    @property
    def description(self) -> str:
        return "Example query operation."

    @property
    def params(self) -> dict:
        return {
            "query": {"type": "string", "description": "Query string", "required": True},
        }

    def execute(self, params: dict) -> ToolResult:
        try:
            # Example: Call your integration's method
            result = self._integration.example_method(params["query"])
            return ToolResult(
                success=True,
                message=f"Query completed: {result}",
                data={"result": result},
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Error in query: {e}")


class ExampleActionTool(Tool):
    """Example tool demonstrating an action operation."""
    def __init__(self, integration):
        self._integration = integration

    @property
    def name(self) -> str:
        return "example_action"

    @property
    def description(self) -> str:
        return "Perform an example action."

    @property
    def params(self) -> dict:
        return {
            "action": {"type": "string", "description": "Action to perform", "required": True},
            "value":  {"type": "string", "description": "Value for action", "required": False},
        }

    def execute(self, params: dict) -> ToolResult:
        try:
            # Example: Call your integration's method
            result = self._integration.example_action(params["action"], params.get("value"))
            return ToolResult(
                success=True,
                message=f"Action completed: {result}",
                data={"result": result},
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Error in action: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Directive
# ──────────────────────────────────────────────────────────────────────────────

class TemplateDirective(BaseDirective):
    """
    A template directive that bundles tools with a system prompt.

    You can customize the system prompt by passing a custom string to
    the constructor, or by overriding the system_prompt() method.
    """

    def __init__(
        self,
        integration,
        system_prompt: str | None = None,
    ) -> None:
        # Create tools that wrap your integration's methods
        # ADAPT THESE TO MATCH YOUR INTEGRATION'S ACTUAL METHODS
        tools = [
            ExampleQueryTool(integration),
            ExampleActionTool(integration),
            # Add more tools as needed for your integration
        ]
        default_prompt = (
            "You are a helpful assistant. Use the available tools to assist the user.\n"
            "Always reply in the same language the user writes in."
        )
        final_prompt = system_prompt or default_prompt

        super().__init__(tools=tools, system_prompt=final_prompt)


__all__ = ["TemplateDirective", "ExampleQueryTool", "ExampleActionTool"]