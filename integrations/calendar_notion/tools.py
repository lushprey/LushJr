"""
integrations/calendar_notion/tools.py
─────────────────────────────────────
Calendar tools for Notion integration.
Each tool wraps the NotionCalendarIntegration to provide the Tool interface.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from integrations.base import Tool, CalendarIntegration

logger = logging.getLogger(__name__)


class QueryEventsToolNotion(Tool):
    """Tool for querying calendar events in a date range."""
    
    def __init__(self, calendar: CalendarIntegration):
        self.calendar = calendar
    
    @property
    def name(self) -> str:
        return "query_events"
    
    @property
    def description(self) -> str:
        return "Query calendar events between two dates"
    
    @property
    def required_params(self) -> list[str]:
        return ["date_start", "date_end"]
    
    def execute(self, params: Dict[str, Any]) -> str:
        try:
            date_start = params.get("date_start")
            date_end = params.get("date_end")
            
            if not date_start or not date_end:
                return "❌ Error: date_start and date_end are required"
            
            events = self.calendar.query_events(date_start, date_end)
            
            if not events:
                return f"📅 No events found between {date_start} and {date_end}"
            
            response = f"📅 Events ({len(events)} found):\n"
            for event in events:
                time_str = ""
                if event.time_start:
                    time_str = f" at {event.time_start}"
                    if event.time_end:
                        time_str += f"-{event.time_end}"
                
                location_str = ""
                if event.location:
                    location_str = f"📍 {event.location}"
                
                response += f"\n• **{event.title}** ({event.date_start}{time_str}){location_str}"
                if event.description:
                    response += f"\n  _{event.description}_"
            
            return response
        except Exception as e:
            logger.error(f"Error querying events: {e}")
            return f"❌ Error querying events: {str(e)}"


class CreateEventToolNotion(Tool):
    """Tool for creating calendar events."""
    
    def __init__(self, calendar: CalendarIntegration):
        self.calendar = calendar
    
    @property
    def name(self) -> str:
        return "create_event"
    
    @property
    def description(self) -> str:
        return "Create a new calendar event"
    
    @property
    def required_params(self) -> list[str]:
        return ["title", "date_start"]
    
    def execute(self, params: Dict[str, Any]) -> str:
        try:
            title = params.get("title")
            date_start = params.get("date_start")
            
            if not title or not date_start:
                return "❌ Error: title and date_start are required"
            
            date_end = params.get("date_end")
            time_start = params.get("time_start")
            time_end = params.get("time_end")
            location = params.get("location")
            description = params.get("description")
            
            event = self.calendar.create_event(
                title=title,
                date_start=date_start,
                date_end=date_end,
                time_start=time_start,
                time_end=time_end,
                location=location,
                description=description,
            )
            
            time_str = ""
            if event.time_start:
                time_str = f" at {event.time_start}"
                if event.time_end:
                    time_str += f"-{event.time_end}"
            
            location_str = ""
            if event.location:
                location_str = f" 📍 {event.location}"
            
            return f"✅ Event created: **{event.title}** on {event.date_start}{time_str}{location_str}"
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return f"❌ Error creating event: {str(e)}"


class UpdateEventToolNotion(Tool):
    """Tool for updating calendar events."""
    
    def __init__(self, calendar: CalendarIntegration):
        self.calendar = calendar
    
    @property
    def name(self) -> str:
        return "update_event"
    
    @property
    def description(self) -> str:
        return "Update an existing calendar event"
    
    @property
    def required_params(self) -> list[str]:
        return ["event_id"]
    
    def execute(self, params: Dict[str, Any]) -> str:
        try:
            event_id = params.get("event_id")
            
            if not event_id:
                return "❌ Error: event_id is required"
            
            # All other params are optional
            title = params.get("title")
            date_start = params.get("date_start")
            date_end = params.get("date_end")
            time_start = params.get("time_start")
            time_end = params.get("time_end")
            location = params.get("location")
            description = params.get("description")
            
            event = self.calendar.update_event(
                event_id=event_id,
                title=title,
                date_start=date_start,
                date_end=date_end,
                time_start=time_start,
                time_end=time_end,
                location=location,
                description=description,
            )
            
            time_str = ""
            if event.time_start:
                time_str = f" at {event.time_start}"
                if event.time_end:
                    time_str += f"-{event.time_end}"
            
            return f"✅ Event updated: **{event.title}** on {event.date_start}{time_str}"
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return f"❌ Error updating event: {str(e)}"


class DeleteEventToolNotion(Tool):
    """Tool for deleting calendar events."""
    
    def __init__(self, calendar: CalendarIntegration):
        self.calendar = calendar
    
    @property
    def name(self) -> str:
        return "delete_event"
    
    @property
    def description(self) -> str:
        return "Delete a calendar event"
    
    @property
    def required_params(self) -> list[str]:
        return ["event_id"]
    
    def execute(self, params: Dict[str, Any]) -> str:
        try:
            event_id = params.get("event_id")
            
            if not event_id:
                return "❌ Error: event_id is required"
            
            self.calendar.delete_event(event_id=event_id)
            return f"✅ Event deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return f"❌ Error deleting event: {str(e)}"
