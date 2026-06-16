"""
integrations/base.py
────────────────────
Abstract interfaces and base implementations for the LushJr plugin system.

This file contains:
1. Abstract interfaces that define contracts for all plugin types
2. Optional base implementations that provide common functionality

Plugin types:
  - AIProvider    → AI inference backend (Nvidia, OpenAI, Anthropic…)
  - CalendarIntegration → Calendar backend (Notion, Google, iCal…)
  - Directive     → Groups tools + system prompt for a use-case
  - Tool          → A single action the bot can perform
  - PlatformBot   → Messaging platform (Telegram, Discord, WhatsApp…)

Base implementations (provided as conveniences):
  - BaseAIProvider    → HTTP client setup for OpenAI-compatible APIs
  - BaseIntegration   → Base class for all integration types
  - BasePlatformBot   → Simple run loop for platform bots
  - BaseDirective     → Configurable system prompt for directives
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx


# ──────────────────────────────────────────────────────────────────────────────
# Base Integration (for all integration types)
# ──────────────────────────────────────────────────────────────────────────────

class BaseIntegration(ABC):
    """Base class for all integrations in the LushJr bot system.

    This provides a common foundation for all integration types (AI providers,
    calendar integrations, platform bots, etc.) to ensure consistency and
    reduce boilerplate code.
    """

    def __init__(self) -> None:
        """Initialize the base integration."""
        pass


# ──────────────────────────────────────────────────────────────────────────────
# HTTP Client Base (for integrations that make HTTP requests)
# ──────────────────────────────────────────────────────────────────────────────

class BaseHttpClient(BaseIntegration):
    """Base class for integrations that make HTTP requests with bearer token authentication.

    Provides a shared httpx.Client instance with proper authentication headers.
    Integrations should inherit from this class when they need to make HTTP requests
    to APIs that use bearer token authentication.
    """
    def __init__(self, token: str, api_base: str):
        super().__init__()
        self.token = token
        self.api_base = api_base.rstrip('/')
        self._client = httpx.Client(
            base_url=self.api_base,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            timeout=30.0,
        )


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
            send(params["to"], params.get("subject", ""), params.get("body", ""))
            return ToolResult(success=True, message=f"Email sent to {params['to']}")
    """

    # ── Required class attributes ─────────────────────

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

    # ── Derived helpers (no need to override) ───────────────

    @property
    def required_params(self) -> list[str]:
        return [k for k, v in self.params.items() if v.get("required", False)]

    @property
    def optional_params(self) -> list[str]:
        return [k for k, v in self.params.items() if not v.get("required", False)]

    # ── Interface ──────────────────────────────────────────

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


class BaseDirective(Directive):
    """Base implementation for Directive that allows system prompt to be configured."""
    def __init__(self, tools: list[Tool], system_prompt: str = "You are a helpful AI assistant."):
        self._tools = tools
        self._system_prompt = system_prompt

    def tools(self) -> list[Tool]:
        return self._tools

    def system_prompt(self) -> str:
        return self._system_prompt


# ──────────────────────────────────────────────────────────────────────────────
# Calendar Event (Platform-agnostic)
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


# ──────────────────────────────────────────────────────────────────────────────
# Calendar Integration Interface
# ──────────────────────────────────────────────────────────────────────────────

class CalendarIntegration(ABC):
    """
    Calendar integration backend for reading and writing calendar events.

    Implement this to swap calendar backends (Notion, Google Calendar, iCal, etc.)
    without changing the rest of the bot's logic.
    """

    @abstractmethod
    def query_events(self, date_start: str, date_end: str) -> list[CalendarEvent]:
        """Query events within a date range (inclusive)."""
        ...

    @abstractmethod
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
        """Create a new calendar event."""
        ...

    @abstractmethod
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
        """Update an existing calendar event."""
        ...

    @abstractmethod
    def delete_event(self, event_id: str) -> None:
        """Delete/Archive a calendar event."""
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


class BaseAIProvider(BaseHttpClient, AIProvider):
    """Base implementation for AIProvider that handles HTTP client setup for OpenAI-compatible APIs.

    Inherits from BaseHttpClient for shared HTTP functionality.
    """
    def __init__(self, api_key: str, api_base: str, model: str, temperature: float = 0.7):
        super().__init__(token=api_key, api_base=api_base)
        self.model = model
        self.temperature = temperature

    def chat(self, message: str, system_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": self.temperature,
        }
        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def choose_tools(
        self,
        message: str,
        tools: list[Tool],
        system_prompt: str,
    ) -> list[ToolCall]:
        # This is a complex task; we provide a simple baseline that returns no tools.
        # Subclasses should override this to provide actual tool selection.
        return [ToolCall(tool_name="chat", params={})]


# ──────────────────────────────────────────────────────────────────────────────
# Platform Bot
# ──────────────────────────────────────────────────────────────────────────────

class PlatformBot(ABC):
    """Messaging platform adapter."""

    @abstractmethod
    def run(self) -> None:
        """Start the bot and block until stopped."""
        ...


class BasePlatformBot(BaseIntegration, PlatformBot):
    """Base implementation for PlatformBot that provides a simple run loop."""
    def __init__(self, processor: MessageProcessor):
        super().__init__()
        self.processor = processor

    def run(self) -> None:
        # This is a placeholder; subclasses should implement actual platform-specific logic.
        raise NotImplementedError("Subclasses must implement run() for their specific platform")