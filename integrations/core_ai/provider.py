"""
integrations/core_ai/provider.py
─────────────────────────────────
AI provider backed by Nvidia's OpenAI-compatible API.

Swap this file (or create a parallel one) to use a different model
provider — just implement AIProvider from integrations.base.

Multi-tool support
------------------
choose_tools() first attempts native function-calling (faster, more
reliable). If the API doesn't support it, it falls back to asking the
model to return JSON directly.  Either way, it may return *multiple*
ToolCall objects so the processor can chain actions automatically.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from openai import OpenAI

from integrations.base import AIProvider, Tool, ToolCall

logger = logging.getLogger(__name__)


class NvidiaAIProvider(AIProvider):
    """
    AIProvider that uses Nvidia's OpenAI-compatible inference endpoint.

    Parameters
    ----------
    api_key : str
        NVIDIA_API_KEY
    model : str, default "meta/llama-3.3-70b-instruct"
        Model slug to use for inference.
    temperature : float, default 0.7
        Sampling temperature for chat responses.
    api_base : str, default "https://integrate.api.nvidia.com/v1"
        Base URL for the API endpoint.
    """

    DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"

    def __init__(
        self,
        api_key: str,
        model: str = "meta/llama-3.3-70b-instruct",
        temperature: float = 0.7,
        api_base: str = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        base_url = api_base or self.DEFAULT_BASE_URL
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    # ──────────────────────────────────────────────────────────────────────
    # AIProvider interface
    # ──────────────────────────────────────────────────────────────────────

    def chat(self, message: str, system_prompt: str) -> str:
        """Return a free-form text reply."""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": message},
            ],
            temperature=self.temperature,
            max_tokens=1024,
        )
        return completion.choices[0].message.content.strip()

    def choose_tools(
        self,
        message:       str,
        tools:         list[Tool],
        system_prompt: str,
    ) -> list[ToolCall]:
        """
        Ask the model which tool(s) to call for this message.

        Returns a list so the processor can chain multiple actions
        (e.g. the user asks to delete 5 events → 5 delete_event calls).

        Falls back to JSON parsing if function-calling is unavailable.
        """
        functions = [self._tool_to_function(t) for t in tools]

        # ── Attempt native function calling ─────────────────────────────
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": message},
                ],
                functions=functions,
                temperature=0.2,  # Lower temperature for more reliable tool selection
                max_tokens=800,
            )
            msg = completion.choices[0].message
            if msg.function_call:
                name   = msg.function_call.name
                params = json.loads(msg.function_call.arguments or "{}")
                return [ToolCall(tool_name=name, params=params)]

        except Exception as exc:
            logger.warning("Function calling unavailable (%s), using JSON fallback.", exc)

        # ── JSON fallback ────────────────────────────────────────────────
        return self._choose_tools_json(message, tools, system_prompt)

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────

    def _tool_to_function(self, tool: Tool) -> dict:
        """Convert a Tool into an OpenAI function-calling schema."""
        properties: dict[str, Any] = {}
        for param_name, meta in tool.params.items():
            properties[param_name] = {
                "type":        meta.get("type", "string"),
                "description": meta.get("description", ""),
            }
        return {
            "name":        tool.name,
            "description": tool.description,
            "parameters": {
                "type":       "object",
                "properties": properties,
                "required":   tool.required_params,
            },
        }

    def _choose_tools_json(
        self,
        message:       str,
        tools:         list[Tool],
        system_prompt: str,
    ) -> list[ToolCall]:
        """
        Fallback: ask the model to emit JSON describing one or more tool calls.

        The model is instructed to return an array, enabling chained actions.
        """
        today      = datetime.now().strftime("%Y-%m-%d")
        day_name   = datetime.now().strftime("%A")
        tool_lines = "\n".join(
            f"  - {t.name}: {t.description}  "
            f"(required: {t.required_params}, optional: {t.optional_params})"
            for t in tools
        )

        fallback_system = (
            f"{system_prompt}\n\n"
            f"Today is {today} ({day_name}).\n\n"
            "Available tools:\n"
            f"{tool_lines}\n\n"
            "Respond with ONLY a JSON array of tool calls.  "
            "You may include multiple entries when the request requires "
            "chained actions (e.g. deleting several events).  "
            "Use the 'chat' tool when no calendar action is needed.\n\n"
            "Format:\n"
            '[\n'
            '  {"tool": "tool_name", "params": {"key": "value"}},\n'
            '  ...\n'
            ']'
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": fallback_system},
                {"role": "user",   "content": message},
            ],
            temperature=0.2,  # Lower temperature for more reliable JSON output
            max_tokens=800,
        )

        raw = (completion.choices[0].message.content or "").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        if not raw:
            logger.warning("AI returned empty response — defaulting to chat.")
            return [ToolCall(tool_name="chat", params={})]

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Could not parse AI JSON %r — defaulting to chat.", raw)
            return [ToolCall(tool_name="chat", params={})]

        # Accept both a single object and an array
        if isinstance(data, dict):
            data = [data]

        calls: list[ToolCall] = []
        for item in data:
            name   = item.get("tool", "chat")
            params = item.get("params", {})
            calls.append(ToolCall(tool_name=name, params=params))

        return calls or [ToolCall(tool_name="chat", params={})]


__all__ = ["NvidiaAIProvider"]