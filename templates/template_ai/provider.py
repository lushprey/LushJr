"""
integrations/my_ai/provider.py
───────────────────────────────
Custom AI provider implementation.

This template shows how to create an AI provider that integrates with
any LLM service (OpenAI, Anthropic, local models, etc).

Key responsibilities:
1. Implement chat() for free-form text responses
2. Implement choose_tools() for tool selection (with fallback to JSON)
3. Handle API calls and error handling

To use this template:
1. Replace 'my_ai' with your actual provider name
2. Modify __init__ to accept your API's specific configuration
3. Implement the chat and choose_tools methods for your API
4. Update the factory function in __init__.py
"""

import json
import logging
from typing import Any

from integrations.base import AIProvider, Tool, ToolCall

logger = logging.getLogger(__name__)


class MyAIProvider(AIProvider):
    """
    Custom AI provider for [YOUR_PROVIDER_NAME].

    Parameters
    ----------
    api_key : str
        API key for authentication
    model : str
        Model identifier/name to use
    temperature : float, default 0.7
        Sampling temperature (0.0–2.0)
    api_base : str, optional
        Base URL for the API endpoint (if applicable)
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        api_base: str = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.api_base = api_base

        # TODO: Initialize your API client here
        # Examples:
        #   self.client = openai.OpenAI(api_key=api_key)
        #   self.client = anthropic.Anthropic(api_key=api_key)
        #   self.client = httpx.Client(base_url=api_base, headers={"Authorization": f"Bearer {api_key}"})

    # ──────────────────────────────────────────────────────────────────────
    # AIProvider interface (REQUIRED)
    # ──────────────────────────────────────────────────────────────────────

    def chat(self, message: str, system_prompt: str) -> str:
        """
        Generate a free-form text reply.

        Called when the user's message doesn't require any tools
        or after tools have been executed for post-processing.

        Args:
            message: User message (or combined tool results)
            system_prompt: System instructions for the AI

        Returns:
            Generated text response
        """
        # TODO: Implement your API call here
        # Example for OpenAI-compatible:
        #   response = self.client.chat.completions.create(
        #       model=self.model,
        #       messages=[
        #           {"role": "system", "content": system_prompt},
        #           {"role": "user", "content": message},
        #       ],
        #       temperature=self.temperature,
        #       max_tokens=1024,
        #   )
        #   return response.choices[0].message.content.strip()

        raise NotImplementedError("Implement chat() for your AI provider")

    def choose_tools(
        self,
        message: str,
        tools: list[Tool],
        system_prompt: str,
    ) -> list[ToolCall]:
        """
        Analyze the user message and determine which tool(s) to call.

        Can return:
        - Multiple ToolCall objects for chained actions
        - A single ToolCall with tool_name="chat" if no tools needed
        - Empty list (will be converted to chat tool by processor)

        Strategy options:
        1. Native function calling (faster, more reliable if supported)
        2. JSON mode (ask model to return structured JSON)
        3. Prompt engineering (construct a carefully worded prompt)

        Args:
            message: User message
            tools: List of available Tool objects
            system_prompt: System instructions

        Returns:
            List of ToolCall objects (one or more)
        """
        # TODO: Implement your tool selection strategy
        #
        # OPTION 1: Native function calling (recommended if supported)
        # try:
        #     response = self.client.chat.completions.create(
        #         model=self.model,
        #         messages=[...],
        #         functions=[self._tool_to_function(t) for t in tools],
        #         temperature=0.2,  # Lower for more reliable selection
        #     )
        #     if response.choices[0].message.function_call:
        #         name = response.choices[0].message.function_call.name
        #         params = json.loads(response.choices[0].message.function_call.arguments)
        #         return [ToolCall(tool_name=name, params=params)]
        # except Exception as e:
        #     logger.warning("Function calling failed: %s, falling back to JSON", e)
        #
        # OPTION 2: JSON mode (fallback)
        # return self._choose_tools_json(message, tools, system_prompt)

        # For now, default to chat (no tool use)
        return [ToolCall(tool_name="chat", params={})]

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers (optional)
    # ──────────────────────────────────────────────────────────────────────

    def _tool_to_function(self, tool: Tool) -> dict[str, Any]:
        """
        Convert a Tool to function calling schema (OpenAI format).

        Adapt the format for your API if needed.
        """
        properties: dict[str, Any] = {}
        for param_name, meta in tool.params.items():
            properties[param_name] = {
                "type": meta.get("type", "string"),
                "description": meta.get("description", ""),
            }

        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": tool.required_params,
            },
        }

    def _choose_tools_json(
        self,
        message: str,
        tools: list[Tool],
        system_prompt: str,
    ) -> list[ToolCall]:
        """
        Fallback: ask the model to return JSON with tool calls.

        Returns a list to enable chained actions.
        """
        tool_descriptions = "\n".join(
            f"  - {t.name}: {t.description} "
            f"(required: {t.required_params}, optional: {t.optional_params})"
            for t in tools
        )

        json_prompt = (
            f"{system_prompt}\n\n"
            f"Available tools:\n{tool_descriptions}\n\n"
            "Respond with ONLY a JSON array of tool calls. "
            "You may include multiple entries for chained actions.\n\n"
            "Format:\n"
            '[\n'
            '  {"tool": "tool_name", "params": {"key": "value"}},\n'
            '  ...\n'
            ']'
        )

        # TODO: Call your API with json_prompt
        # response = self.client.chat.completions.create(
        #     model=self.model,
        #     messages=[
        #         {"role": "system", "content": json_prompt},
        #         {"role": "user", "content": message},
        #     ],
        #     temperature=0.2,
        # )
        # raw = response.choices[0].message.content.strip()

        raw = ""  # Placeholder
        raw = raw.replace("```json", "").replace("```", "").strip()

        if not raw:
            logger.warning("Empty response from model")
            return [ToolCall(tool_name="chat", params={})]

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse JSON: %s", e)
            return [ToolCall(tool_name="chat", params={})]

        # Accept both single object and array
        if isinstance(data, dict):
            data = [data]

        calls: list[ToolCall] = []
        for item in data:
            name = item.get("tool", "chat")
            params = item.get("params", {})
            calls.append(ToolCall(tool_name=name, params=params))

        return calls or [ToolCall(tool_name="chat", params={})]


__all__ = ["MyAIProvider"]