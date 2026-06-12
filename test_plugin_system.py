#!/usr/bin/env python3
"""
test_plugin_system.py
─────────────────────
Quick verification script for the plugin system.
Tests that all plugins can be loaded and have correct structure.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🧪 LushJr Bot - Plugin System Verification")
print("=" * 70)

# Test 1: Plugin registry
print("\n[1/5] Testing plugin registry...")
try:
    from integrations import load_plugin, DEFAULT_PLUGINS
    print(f"  ✅ Plugin registry imported")
    print(f"  ✅ Default plugins: {DEFAULT_PLUGINS}")
except Exception as e:
    print(f"  ❌ Failed to import plugin registry: {e}")
    sys.exit(1)

# Test 2: Base abstractions
print("\n[2/5] Testing base abstractions...")
try:
    from integrations.base import Tool, Directive, AIProvider, CalendarIntegration, PlatformBot, ToolCall
    print(f"  ✅ All base abstractions imported")
except Exception as e:
    print(f"  ❌ Failed to import base abstractions: {e}")
    sys.exit(1)

# Test 3: MessageProcessor
print("\n[3/5] Testing message processor...")
try:
    from core.processor import MessageProcessor
    print(f"  ✅ MessageProcessor imported")
except Exception as e:
    print(f"  ❌ Failed to import MessageProcessor: {e}")
    sys.exit(1)

# Test 4: Core AI plugin
print("\n[4/5] Testing core_ai plugin...")
try:
    from integrations.core_ai import create_ai_provider, NvidiaAIProvider
    print(f"  ✅ Core AI plugin imported")
    print(f"  ✅ Factory function: create_ai_provider")
except Exception as e:
    print(f"  ❌ Failed to import core_ai plugin: {e}")
    sys.exit(1)

# Test 5: Calendar Notion plugin structure
print("\n[5/5] Testing calendar_notion plugin structure...")
try:
    from integrations.calendar_notion import create_calendar_integration
    from integrations.calendar_notion.integration import NotionCalendarIntegration
    from integrations.calendar_notion.directive import CalendarDirective
    from integrations.calendar_notion.tools import (
        QueryEventsToolNotion,
        CreateEventToolNotion,
        UpdateEventToolNotion,
        DeleteEventToolNotion,
    )
    print(f"  ✅ Calendar Notion plugin imported")
    print(f"  ✅ Integration class: NotionCalendarIntegration")
    print(f"  ✅ Directive class: CalendarDirective")
    print(f"  ✅ Tool classes:")
    print(f"     - QueryEventsToolNotion")
    print(f"     - CreateEventToolNotion")
    print(f"     - UpdateEventToolNotion")
    print(f"     - DeleteEventToolNotion")
except Exception as e:
    print(f"  ❌ Failed to import calendar_notion plugin: {e}")
    sys.exit(1)

# Test 6: Try loading plugins (will fail on env vars, but that's OK)
print("\n[6/6] Testing plugin loading (dry run)...")
try:
    # Check if env vars are set
    required = ["TELEGRAM_TOKEN", "NVIDIA_API_KEY", "NOTION_TOKEN", "DATABASE_ID"]
    missing = [v for v in required if not os.getenv(v)]
    
    if missing:
        print(f"  ⚠️  Missing environment variables: {', '.join(missing)}")
        print(f"  ℹ️  (This is expected - plugins need actual credentials)")
    else:
        print(f"  ✅ All environment variables set")
        ai_provider = load_plugin('ai')
        calendar_integration, calendar_directive = load_plugin('calendar')
        print(f"  ✅ AI provider loaded: {type(ai_provider).__name__}")
        print(f"  ✅ Calendar integration loaded: {type(calendar_integration).__name__}")
        print(f"  ✅ Calendar directive loaded: {type(calendar_directive).__name__}")
        
        # Check directive structure
        tools = calendar_directive.get_tools()
        system_prompt = calendar_directive.get_system_prompt()
        print(f"  ✅ Directive has {len(tools)} tools")
        print(f"     Available tools:")
        for tool in tools:
            print(f"       - {tool.name}: {tool.description}")
        print(f"  ✅ System prompt length: {len(system_prompt)} chars")
except ValueError as e:
    print(f"  ⚠️  Cannot load plugins (missing env vars): {e}")
    print(f"  ℹ️  (This is expected - set env vars to fully test)")
except Exception as e:
    print(f"  ❌ Failed to load plugins: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ All plugin system tests passed!")
print("=" * 70)
print("\nNext steps:")
print("1. Set environment variables: TELEGRAM_TOKEN, NVIDIA_API_KEY, NOTION_TOKEN, DATABASE_ID")
print("2. Run: python main.py")
print("\nTo swap plugins:")
print("1. Edit integrations/__init__.py DEFAULT_PLUGINS")
print("2. Or modify config.yaml (if implemented)")
print("=" * 70)
