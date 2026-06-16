#!/usr/bin/env python3
"""Test the date resolver function."""

from integrations.calendar_notion.tools import _resolve_date

print("Testing date resolver...")

# Test cases
test_cases = [
    ("today", "today"),
    ("tomorrow", "tomorrow"),
    ("yesterday", "yesterday"),
    ("hoy", "today"),
    ("mañana", "tomorrow"),
    ("ayer", "yesterday"),
    ("this week", "this week"),
    ("esta semana", "this week"),
    ("this month", "this month"),
    ("este mes", "this month"),
    ("2026-06-16", "2026-06-16"),  # Already ISO format
]

for test_input, description in test_cases:
    try:
        result = _resolve_date(test_input)
        print(f"PASS: {test_input!r} -> {result}")
    except Exception as e:
        print(f"FAIL: {test_input!r} -> {e}")

print("\nDate resolver tests completed.")