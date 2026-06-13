"""
integrations/base.py
────────────────────
Abstract interfaces for the LushJr plugin system.

Every plugin must implement the relevant abstract class here.
This file is the contract — don't change it unless you're adding
a new plugin type.

Plugin types:
  - AIProvider    → AI inference backend (Nvidia, OpenAI, Anthropic…)
  - CalendarIntegration → Calendar backend (Notion, Google, iCal…)
  - Directive     → Groups tools + system prompt for a use-case
  - Tool          → A single action the bot can perform
  - PlatformBot   → Messaging platform (Telegram, Discord, WhatsApp…)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# Tool
# ──────────────────────────────────────────────────────────────────────────────

class Tool(ABC):
    """
    A single action the bot can execute.

    Implement this to add new capabilities to a Directive.

    Example
    -------
    class SendEmailTool(Tool):
        name        = "send_email"
        description = "Send an email to a recipient"
        params      = {
            "to":      {"type": "string", "description": "Recipient address", "required": True},
            "subject": {"type": "string", "description": "Email subject",     "required": True},
            "body":    {"type": "string", "description": "Email body",        "required": False},
        }

        def execute(self, params):
            send(params["to"], params["subject"], params.get("body", ""))
            return ToolResult(success=True, message=f"Email sent to {params['to']}")
    """

    # ── Required class attributes ────────────────────────────────────────────

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique snake_case identifier, e.g. 'create_event'."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """One-sentence description for the AI to understand what this does."""
        ...

    @property
    @abstractmethod
    def params(self) -> dict[str, dict]:
        """
        Parameter schema.  Keys are param names; values are dicts with:
          - type        (str)  : "string" | "integer" | "boolean"
          - description (str)  : what the param means
          - required    (bool) : whether the AI must supply it
        """
        ...

    # ── Derived helpers (no need to override) ───────────────────────────────

    @property
    def required_params(self) -> list[str]:
        return [k for k, v in self.params.items() if v.get("required", False)]

    @property
    def optional_params(self) -> list[str]:
        return [k for k, v in self.params.items() if not v.get("required", False)]

    # ── Interface ────────────────────────────────────────────────────────────

    @abstractmethod
    def execute(self, params: dict[str, Any]) -> "ToolResult":
        """Run the tool and return a ToolResult."""
        ...


@dataclass
class ToolResult:
    """Standardised return value from Tool.execute()."""
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# Directive
# ──────────────────────────────────────────────────────────────────────────────

class Directive(ABC):
    """
    A Directive bundles a set of Tools with a system prompt.

    Think of it as a "skill pack" — it defines *what the bot can do*
    and *how the AI should behave* in a given context.

    To add a new use-case (e.g. CRM, e-commerce), create a new Directive
    without touching any existing code.
    """

    @abstractmethod
    def tools(self) -> list[Tool]:
        """Return all tools available in this directive."""
        ...

    @abstractmethod
    def system_prompt(self) -> str:
        """
        System prompt injected into every AI call.
        Should describe the bot's persona, responsibilities, and available tools.
        """
        ...


# ──────────────────────────────────────────────────────────────────────────────
# AI Provider
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ToolCall:
    """A single tool invocation chosen by the AI."""
    tool_name: str
    params:    dict[str, Any]


class AIProvider(ABC):
    """
    AI inference backend.

    Implement this to swap the underlying model without changing
    any other part of the bot.
    """

    @abstractmethod
    def chat(self, message: str, system_prompt: str) -> str:
        """Generate a free-form text reply."""
        ...

    @abstractmethod
    def choose_tools(
        self,
        message:       str,
        tools:         list[Tool],
        system_prompt: str,
    ) -> list[ToolCall]:
        """
        Analyse the user message and return one *or more* tool calls.

        Returning multiple calls lets the AI chain actions automatically
        (e.g. "delete all events this month" → several delete_event calls).

        If the message doesn't match any tool, return:
            [ToolCall(tool_name="chat", params={})]
        """
        ...


# ──────────────────────────────────────────────────────────────────────────────
# Calendar Integration  (domain-specific, kept separate from the generic layer)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class CalendarEvent:
    """Platform-agnostic calendar event."""
    id:          str
    title:       str
    date_start:  str                  # ISO-8601  "YYYY-MM-DD"
    date_end:    str | None = None
    time_start:  str | None = None    # "HH:MM"
    time_end:    str | None = None    # "HH:MM"
    location:    str | None = None
    description: str | None = None


class CalendarIntegration(ABC):
    """Calendar storage backend."""

    @abstractmethod
    def query_events(self, date_start: str, date_end: str) -> list[CalendarEvent]:
        """Return events whose start date falls in [date_start, date_end]."""
        ...

    @abstractmethod
    def create_event(
        self,
        title:       str,
        date_start:  str,
        date_end:    str | None = None,
        time_start:  str | None = None,
        time_end:    str | None = None,
        location:    str | None = None,
        description: str | None = None,
    ) -> CalendarEvent:
        ...

    @abstractmethod
    def update_event(
        self,
        event_id:    str,
        title:       str | None = None,
        date_start:  str | None = None,
        date_end:    str | None = None,
        time_start:  str | None = None,
        time_end:    str | None = None,
        location:    str | None = None,
        description: str | None = None,
    ) -> CalendarEvent:
        ...

    @abstractmethod
    def delete_event(self, event_id: str) -> None:
        ...


# ──────────────────────────────────────────────────────────────────────────────
# Platform Bot
# ──────────────────────────────────────────────────────────────────────────────

class PlatformBot(ABC):
    """Messaging platform adapter."""

    @abstractmethod
    def run(self) -> None:
        """Start the bot and block until stopped."""
        ...