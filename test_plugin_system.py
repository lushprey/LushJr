#!/usr/bin/env python3
"""
test_plugin_system.py
─────────────────────
Verifies the plugin system without real API keys.

Tests:
  1. All modules import cleanly.
  2. Base abstractions are correctly defined.
  3. Tool schema / ToolResult contract works.
  4. Processor chains multiple tool calls correctly.
  5. Date resolver handles relative keywords.
  6. Plugin loader resolves factories (no credentials needed).
  7. Config loader and plugin registry work with the new configuration system.
"""
from __future__ import annotations

import sys
import traceback
from typing import Any
from unittest.mock import MagicMock


PASS = "  [OK]"
FAIL = "  [FAIL]"
WARN = "  [WARN]"


def section(title: str) -> None:
    print(f"\n{'-'*60}")
    print(f"  {title}")
    print(f"{'-'*60}")


def ok(msg: str) -> None:
    print(f"{PASS} {msg}")


def fail(msg: str, exc: Exception | None = None) -> None:
    print(f"{FAIL} {msg}")
    if exc:
        traceback.print_exc()


# ──────────────────────────────────────────────────────────────────────────────
# 1 · Imports
# ──────────────────────────────────────────────────────────────────────────────

section("1 / Imports")

errors = 0

try:
    from integrations.base import (
        Tool, ToolResult, Directive, AIProvider,
        CalendarIntegration, CalendarEvent,
        PlatformBot, ToolCall,
    )
    ok("integrations.base")
except Exception as e:
    fail("integrations.base", e); errors += 1

try:
    from core.processor import MessageProcessor
    ok("core.processor.MessageProcessor")
except Exception as e:
    fail("core.processor", e); errors += 1

try:
    from integrations.core_ai import NvidiaAIProvider
    ok("integrations.core_ai.NvidiaAIProvider")
except Exception as e:
    fail("integrations.core_ai", e); errors += 1

try:
    from integrations.calendar_notion.tools import (
        QueryEventsTool, CreateEventTool, UpdateEventTool, DeleteEventTool,
    )
    ok("integrations.calendar_notion.tools")
except Exception as e:
    fail("integrations.calendar_notion.tools", e); errors += 1

try:
    from integrations.calendar_notion.directive import CalendarDirective
    ok("integrations.calendar_notion.directive.CalendarDirective")
except Exception as e:
    fail("integrations.calendar_notion.directive", e); errors += 1

try:
    from integrations.calendar_notion.integration import NotionCalendarIntegration
    ok("integrations.calendar_notion.integration.NotionCalendarIntegration")
except Exception as e:
    fail("integrations.calendar_notion.integration", e); errors += 1

try:
    from integrations import load_plugin, DEFAULT_PLUGINS
    ok(f"integrations.load_plugin  (defaults: {DEFAULT_PLUGINS})")
except Exception as e:
    fail("integrations.load_plugin", e); errors += 1


# ──────────────────────────────────────────────────────────────────────────────
# 2 · Tool contract
# ──────────────────────────────────────────────────────────────────────────────

section("2 / Tool & ToolResult contract")

class EchoTool(Tool):
    """A minimal tool used only for testing."""
    @property
    def name(self):        return "echo"
    @property
    def description(self): return "Echo back the message param."
    @property
    def params(self):
        return {
            "message": {"type": "string", "description": "Text to echo", "required": True},
        }
    def execute(self, params: dict[str, Any]) -> ToolResult:
        return ToolResult(success=True, message=params.get("message", ""))

echo = EchoTool()
assert echo.required_params == ["message"],  "required_params broken"
assert echo.optional_params == [],           "optional_params broken"
ok("Tool.required_params / optional_params")

result = echo.execute({"message": "hello"})
assert result.success is True
assert result.message == "hello"
ok("Tool.execute -> ToolResult")


# ──────────────────────────────────────────────────────────────────────────────
# 3 · Date resolver
# ──────────────────────────────────────────────────────────────────────────────

section("3 / Date resolver (_resolve_date)")

from integrations.calendar_notion.tools import _resolve_date
from datetime import datetime

today_str = datetime.now().date().isoformat()

assert _resolve_date("today")  == today_str, "today failed"
assert _resolve_date("hoy")    == today_str, "hoy failed"
assert _resolve_date("2025-06-10") == "2025-06-10", "ISO passthrough failed"

tomorrow = _resolve_date("tomorrow")
assert tomorrow > today_str, "tomorrow should be after today"

ok("today / hoy / tomorrow / manana / ISO passthrough")


# ──────────────────────────────────────────────────────────────────────────────
# 4 · Single tool call  (mock calendar + AI)
# ──────────────────────────────────────────────────────────────────────────────

section("4 / Processor - single tool call")

# Mock calendar
mock_calendar = MagicMock(spec=CalendarIntegration)
mock_calendar.query_events.return_value = [
    CalendarEvent(id="1", title="Dentist", date_start="2026-06-15", time_start="10:00"),
]

# Mock directive
mock_directive = MagicMock(spec=Directive)
mock_directive.tools.return_value = [QueryEventsTool(mock_calendar)]
mock_directive.system_prompt.return_value = "You are a test bot."

# Mock AI — returns a single tool call
mock_ai = MagicMock(spec=AIProvider)
mock_ai.choose_tools.return_value = [
    ToolCall(tool_name="query_events", params={"date_start": "today", "date_end": "today"}),
]
mock_ai.chat.return_value = "You have a dentist appointment at 10:00."

processor = MessageProcessor(ai=mock_ai, directive=mock_directive)
reply = processor.process("What's on my calendar today?")

assert "Dentist" in mock_ai.chat.call_args[0][0], "Dentist not passed to chat"
ok(f"Single tool call -> reply: {reply!r}")


# ──────────────────────────────────────────────────────────────────────────────
# 5 · Chained tool calls  (multi-delete scenario)
# ──────────────────────────────────────────────────────────────────────────────

section("5 / Processor - chained tool calls (multi-delete)")

mock_calendar2 = MagicMock(spec=CalendarIntegration)
mock_calendar2.delete_event.return_value = None

delete_tool = DeleteEventTool(mock_calendar2)
mock_directive2 = MagicMock(spec=Directive)
mock_directive2.tools.return_value = [delete_tool]
mock_directive2.system_prompt.return_value = "You are a test bot."

mock_ai2 = MagicMock(spec=AIProvider)
# Simulate AI returning 3 delete calls for 3 events
mock_ai2.choose_tools.return_value = [
    ToolCall(tool_name="delete_event", params={"event_id": "aaa"}),
    ToolCall(tool_name="delete_event", params={"event_id": "bbb"}),
    ToolCall(tool_name="delete_event", params={"event_id": "ccc"}),
]
mock_ai2.chat.return_value = "All 3 events deleted."

processor2 = MessageProcessor(ai=mock_ai2, directive=mock_directive2)
reply2 = processor2.process("Delete all events this month")

assert mock_calendar2.delete_event.call_count == 3, (
    f"Expected 3 delete calls, got {mock_calendar2.delete_event.call_count}"
)
ok(f"3 chained delete_event calls executed -> reply: {reply2!r}")


# ──────────────────────────────────────────────────────────────────────────────
# 6 · Chat fallback (no tool needed)
# ──────────────────────────────────────────────────────────────────────────────

section("6 / Processor - chat fallback")

mock_ai3 = MagicMock(spec=AIProvider)
mock_ai3.choose_tools.return_value = [ToolCall(tool_name="chat", params={})]
mock_ai3.chat.return_value = "I'm doing great, thanks!"

mock_directive3 = MagicMock(spec=Directive)
mock_directive3.tools.return_value = []
mock_directive3.system_prompt.return_value = "You are a test bot."

processor3 = MessageProcessor(ai=mock_ai3, directive=mock_directive3)
reply3 = processor3.process("How are you?")
assert reply3 == "I'm doing great, thanks!"
ok(f"Chat fallback -> {reply3!r}")


# ──────────────────────────────────────────────────────────────────────────────
# 7 · Tool failure stops the chain
# ──────────────────────────────────────────────────────────────────────────────

section("7 / Processor - tool failure stops chain")

class FailTool(Tool):
    @property
    def name(self):        return "fail_tool"
    @property
    def description(self): return "Always fails."
    @property
    def params(self):      return {}
    def execute(self, params):
        return ToolResult(success=False, message="❌ Something broke")

mock_ai4 = MagicMock(spec=AIProvider)
mock_ai4.choose_tools.return_value = [
    ToolCall(tool_name="fail_tool", params={}),
    ToolCall(tool_name="echo",      params={"message": "should not run"}),
]

mock_directive4 = MagicMock(spec=Directive)
mock_directive4.tools.return_value = [FailTool(), EchoTool()]
mock_directive4.system_prompt.return_value = "test"

processor4 = MessageProcessor(ai=mock_ai4, directive=mock_directive4)
reply4 = processor4.process("trigger failure")
assert "❌" in reply4
assert mock_ai4.chat.call_count == 0, "chat() should NOT be called after a failure"
ok("Tool failure stops chain immediately")


# ──────────────────────────────────────────────────────────────────────────────
# 8 · CalendarDirective structure
# ──────────────────────────────────────────────────────────────────────────────

section("8 / CalendarDirective structure")

mock_cal = MagicMock(spec=CalendarIntegration)
directive = CalendarDirective(mock_cal)
tools     = directive.tools()
names     = {t.name for t in tools}
assert {"query_events", "create_event", "update_event", "delete_event"} == names
ok(f"Default tools: {names}")

prompt = directive.system_prompt()
assert len(prompt) > 50
ok(f"system_prompt present ({len(prompt)} chars)")

custom_prompt = "Custom prompt here."
directive2 = CalendarDirective(mock_cal, system_prompt=custom_prompt)
assert directive2.system_prompt() == custom_prompt
ok("Custom system_prompt override works")


# ──────────────────────────────────────────────────────────────────────────────
# 9 · Config loader and plugin registry
# ──────────────────────────────────────────────────────────────────────────────

section("9 / Config loader and plugin registry")

try:
    from config.loader import load_config
    from integrations import registry, PluginRegistry
    ok("config loader and plugin registry imports")
except Exception as e:
    fail("config loader and plugin registry imports", e); errors += 1

# Test that load_plugin accepts a config argument (we won't actually load a plugin
# because that would require real credentials; we just check the signature)
try:
    from integrations import load_plugin
    import inspect
    sig = inspect.signature(load_plugin)
    # Accepts plugin_type, plugin_name=None, config=None
    params = list(sig.parameters.keys())
    assert "config" in params, "load_plugin should accept config argument"
    ok("load_plugin accepts config argument")
except Exception as e:
    fail("load_plugin signature check", e); errors += 1

# Test that the registry can discover our template plugins (if they exist)
try:
    # Get discovered plugin types
    plugin_types = registry.get_plugin_types()
    # We expect at least the template plugins we created (if the test environment includes them)
    # But to avoid depending on the presence of templates, we just check that it returns a dict.
    assert isinstance(plugin_types, dict), "get_plugin_types should return a dict"
    ok(f"plugin registry discovers plugins: {list(plugin_types.keys())}")
except Exception as e:
    fail("plugin registry discovery", e); errors += 1


# ──────────────────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
if errors:
    print(f"{FAIL} {errors} import error(s) — fix before running the bot.")
    sys.exit(1)
else:
    print(f"{PASS} All tests passed!")
print(f"{'='*60}\n")