"""
core/processor.py
─────────────────
Central message processor.

Flow
----
1. Ask the AI which tool(s) to call (may be multiple for chained actions).
2. Execute each tool in sequence.
3. If all tools succeeded, post-process the combined result with the AI
   for a polished, natural-language reply.
4. On any tool failure, return the error immediately.

To swap the AI or directive, change what you pass into __init__.
This class is intentionally generic — it knows nothing about calendars,
Telegram, or any specific integration.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from integrations.base import AIProvider, Directive

logger = logging.getLogger(__name__)


class MessageProcessor:
    """
    Wires an AIProvider and a Directive together.

    Parameters
    ----------
    ai        : Any AIProvider implementation.
    directive : Any Directive implementation (provides tools + system prompt).
    """

    def __init__(self, ai: "AIProvider", directive: "Directive") -> None:
        self.ai        = ai
        self.directive = directive

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def process(self, message: str) -> str:
        """
        Process a user message and return a reply string.

        Supports chained tool calls: the AI can choose more than one tool
        (e.g. deleting multiple events) and all are executed in order.
        """
        tools         = self.directive.tools()
        system_prompt = self.directive.system_prompt()
        tool_map      = {t.name: t for t in tools}

        logger.info("Processing: %r", message)

        # 1. Ask the AI which tool(s) to use
        calls = self.ai.choose_tools(message, tools, system_prompt)
        logger.info("Tool calls chosen: %s", [(c.tool_name, c.params) for c in calls])

        # 2. Handle pure-chat (no tool needed)
        if len(calls) == 1 and calls[0].tool_name == "chat":
            return self.ai.chat(message, system_prompt)

        # 3. Execute each tool and collect results
        results: list[str] = []
        for call in calls:
            if call.tool_name == "chat":
                # Mixed chain: a chat step inside a multi-action sequence
                results.append(self.ai.chat(message, system_prompt))
                continue

            tool = tool_map.get(call.tool_name)
            if tool is None:
                logger.warning("Unknown tool requested: %s", call.tool_name)
                return f"❌ Unknown tool: {call.tool_name}"

            result = tool.execute(call.params)
            logger.info("Tool %r → success=%s  message=%r", call.tool_name, result.success, result.message)

            if not result.success:
                return result.message          # Fail fast on first error

            results.append(result.message)

        # 4. Post-process combined output with AI for a natural reply
        combined = "\n".join(results)
        return self.ai.chat(combined, system_prompt)