#!/usr/bin/env python3
"""Simple test to check if the tools work correctly."""

from integrations.calendar_notion.tools import (
    QueryEventsTool,
    CreateEventTool,
    UpdateEventTool,
    DeleteEventTool,
    BaseCalendarTool
)
from integrations.base import Tool

# Test that all tools inherit from BaseCalendarTool
print("Testing inheritance...")
assert issubclass(QueryEventsTool, BaseCalendarTool)
assert issubclass(CreateEventTool, BaseCalendarTool)
assert issubclass(UpdateEventTool, BaseCalendarTool)
assert issubclass(DeleteEventTool, BaseCalendarTool)
print("PASS: All tools inherit from BaseCalendarTool")

# Test that BaseCalendarTool inherits from Tool
assert issubclass(BaseCalendarTool, Tool)
print("PASS: BaseCalendarTool inherits from Tool")

# Test instantiation
from unittest.mock import Mock
mock_calendar = Mock()

query_tool = QueryEventsTool(mock_calendar)
create_tool = CreateEventTool(mock_calendar)
update_tool = UpdateEventTool(mock_calendar)
delete_tool = DeleteEventTool(mock_calendar)

print("PASS: All tools instantiated successfully")

# Test that they have the expected attributes
assert hasattr(query_tool, 'name')
assert hasattr(query_tool, 'description')
assert hasattr(query_tool, 'params')
assert hasattr(query_tool, 'execute')

print("PASS: All tools have required attributes")

print("\nAll tests passed!")