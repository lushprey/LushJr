"""
integrations/template_ai/provider.py
───────────────────────────────────────
Template AI provider implementation.

This template demonstrates how to create a custom AI provider by inheriting
from BaseAIProvider (defined in integrations.base). BaseAIProvider provides
a basic implementation of chat and choose_tools (which defaults to returning
a chat tool). You can override these methods to add actual AI functionality.

To use this template:
1. Rename the directory 'template_ai' to something like 'my_ai'.
2. Implement your AI logic in the methods below.
3. Ensure the factory in __init__.py returns an instance of your class.
4. Add configuration for your plugin in config.yaml (if needed).
"""

from integrations.base import BaseAIProvider, Tool, ToolCall


class TemplateAIProvider(BaseAIProvider):
    """
    A template AI provider that inherits from BaseAIProvider.

    BaseAIProvider already provides:
    - chat: Uses an httpx client to call an OpenAI-compatible API.
    - choose_tools: Returns a list with a single ToolCall for 'chat' (no tool use).

    If you want to use a different API (e.g., Anthropic, local model), you may
    need to override the chat method and optionally the __init__ to set up
    a different client.

    If you want the AI to be able to select and use tools, override the
    choose_tools method to return appropriate ToolCall instances.
    """

    def __init__(self, api_key: str, model: str = "template/model", temperature: float = 0.7, api_base: str = None):
        """
        Initialize the template AI provider.

        Args:
            api_key: The API key for the AI service.
            model: The model identifier to use.
            temperature: Sampling temperature for chat responses.
            api_base: Base URL for the API endpoint. If None, uses a default
                      (you should set this to your API's base URL).
        """
        # If you want to use the BaseAIProvider's HTTP client (which is
        # configured for OpenAI-compatible APIs), you can call super().__init__
        # with the appropriate parameters. However, for demonstration, we'll
        # just store the parameters and note that the user should implement
        # the actual API calls.
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.api_base = api_base
        # TODO: Set up your actual client here (e.g., openai.AsyncOpenAI, httpx.Client, etc.)
        # For now, we leave the client as None and the methods will raise if called.

    # ──────────────────────────────────────────────────────────────────────
    # AIProvider interface (override as needed)
    # ──────────────────────────────────────────────────────────────────────

    def chat(self, message: str, system_prompt: str) -> str:
        """
        Generate a free-form text reply.

        This template implementation returns a placeholder message.
        Replace this with a call to your AI service.
        """
        # TODO: Implement actual chat completion using your AI service.
        # For example, if using an OpenAI-compatible API:
        #   completion = self.client.chat.completions.create(
        #       model=self.model,
        #       messages=[{"role": "system", "content": system_prompt},
        #                 {"role": "user", "content": message}],
        #       temperature=self.temperature,
        #   )
        #   return completion.choices[0].message.content
        return f"[Template AI] Received message: {message}"

    def choose_tools(
        self,
        message: str,
        tools: list[Tool],
        system_prompt: str,
    ) -> list[ToolCall]:
        """
        Analyse the user message and return tool calls.

        This template implementation returns a chat tool call, indicating
        no tool use. Override this method to implement actual tool selection.

        Args:
            message: The user message.
            tools: List of available tools.
            system_prompt: System prompt for the AI.

        Returns:
            List of ToolCall objects.
        """
        # TODO: Implement tool selection logic.
        # For example, you could use function calling or JSON prompting
        # to determine which tools to use.
        # For now, we default to chat (no tool use).
        return [ToolCall(tool_name="chat", params={})]


__all__ = ["TemplateAIProvider"]