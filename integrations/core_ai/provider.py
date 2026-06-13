"""
integrations/core_ai/provider.py
─────────────────────────────────
"""
import json
import logging
from typing import List

from openai import OpenAI

from core.prompts import (
    render_intent_system,
    render_chat_system,
    render_tool_selection_fallback,
)
from integrations.base import AIProvider, IntentResult, Tool, ToolCall

logger = logging.getLogger(__name__)


class NvidiaAIProvider(AIProvider):

    def __init__(self, api_key: str, model: str = "meta/llama-3.1-8b-instruct"):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
        )
        self.model = model

    # ── Public interface ─────────────────────────────────────────────────────

    def detect_intent(self, message: str, context: dict) -> IntentResult:
        """Legacy method for backward compatibility. Prompt comes from core/prompts.py."""
        system_prompt = render_intent_system(
            fecha_hoy=context.get("fecha_hoy"),
            dia_semana=context.get("dia_semana"),
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.2,
            max_tokens=300,
        )

        raw = completion.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        return IntentResult.from_dict(data)

    def chat(self, message: str, system_prompt: str) -> str:
        """
        Generate freeform chat response.

        The caller (usually MessageProcessor) passes the system prompt.
        For general chat not tied to a directive, render_chat_system() is used.
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        return completion.choices[0].message.content.strip()

    def call_with_tools(
        self,
        message: str,
        tools: List[Tool],
        system_prompt: str,
    ) -> ToolCall:
        """
        Call AI with available tools and return a structured ToolCall.

        The system_prompt comes from the directive (which builds it via core/prompts.py).
        The tool-selection fallback prompt also comes from core/prompts.py.
        """
        functions = self._build_function_schemas(tools)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        # Try native function calling first
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                temperature=0.2,
                max_tokens=500,
            )
            response_message = completion.choices[0].message
            if response_message.function_call:
                tool_name = response_message.function_call.name
                params = json.loads(response_message.function_call.arguments)
                return ToolCall(tool_name=tool_name, params=params)
        except Exception as e:
            logger.warning(f"Function calling failed: {e}. Falling back to JSON parsing.")

        # Fallback: JSON-mode tool selection (prompt built from core/prompts.py)
        return self._call_with_json_fallback(message, tools, system_prompt)

    # ── Private helpers ──────────────────────────────────────────────────────

    def _build_function_schemas(self, tools: List[Tool]) -> list:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param: {"type": "string"}
                        for param in tool.required_params
                    },
                    "required": tool.required_params,
                },
            }
            for tool in tools
        ]

    def _call_with_json_fallback(
        self, message: str, tools: List[Tool], base_system: str
    ) -> ToolCall:
        """Ask the AI to return a JSON tool-selection object."""
        tool_descriptions = "\n".join(
            f"- {t.name}: {t.description} (params: {', '.join(t.required_params)})"
            for t in tools
        )
        fallback_prompt = render_tool_selection_fallback(tool_descriptions, base_system)

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": fallback_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.2,
            max_tokens=500,
        )

        raw = completion.choices[0].message.content or ""
        raw = raw.strip().replace("```json", "").replace("```", "").strip()

        if not raw:
            logger.warning("AI returned empty response, defaulting to chat tool")
            return ToolCall(tool_name="chat", params={})

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response '{raw}': {e}. Defaulting to chat.")
            return ToolCall(tool_name="chat", params={})

        return ToolCall(
            tool_name=data.get("tool", "chat"),
            params=data.get("params", {}),
        )