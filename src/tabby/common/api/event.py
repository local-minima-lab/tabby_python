"""
Event logging types for Tabby.

Defines event structures for tracking completion views, selections, dismissals, etc.
"""

import time
from typing import List, Optional, Literal
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from enum import Enum


class SelectKind(str, Enum):
    """Type of selection made by user."""
    LINE = "line"


class LogEventRequest(BaseModel):
    """Request to log an event."""
    
    # Event type, should be 'view', 'select' or 'dismiss'
    event_type: str = Field(..., alias="type", example="view")
    completion_id: str
    choice_index: int
    view_id: Optional[str] = None
    elapsed: Optional[int] = None
    
    class Config:
        populate_by_name = True  # Allow both 'type' and 'event_type'


class Choice(BaseModel):
    """A completion choice."""
    
    index: int
    text: str


class Message(BaseModel):
    """A chat message."""
    
    role: str
    content: str


class Declaration(BaseModel):
    """A code declaration reference."""
    
    filepath: str
    body: str


class Segments(BaseModel):
    """Context segments for a completion."""
    
    prefix: str
    suffix: Optional[str] = None
    clipboard: Optional[str] = None
    git_url: Optional[str] = None
    declarations: Optional[List[Declaration]] = None
    filepath: Optional[str] = None


class Event(BaseModel):
    """
    Base class for all events.
    
    Uses discriminated union pattern for different event types.
    """
    
    type: str = Field(..., description="Event type discriminator")
    
    class Config:
        # Use discriminator for proper serialization
        use_enum_values = True


class ViewEvent(Event):
    """Event when a completion is viewed."""
    
    type: Literal["view"] = "view"
    completion_id: str
    choice_index: int
    view_id: Optional[str] = None


class SelectEvent(Event):
    """Event when a completion is selected."""
    
    type: Literal["select"] = "select"
    completion_id: str
    choice_index: int
    kind: Optional[SelectKind] = None
    view_id: Optional[str] = None
    elapsed: Optional[int] = None


class DismissEvent(Event):
    """Event when a completion is dismissed."""
    
    type: Literal["dismiss"] = "dismiss"
    completion_id: str
    choice_index: int
    view_id: Optional[str] = None
    elapsed: Optional[int] = None


class CompletionEvent(Event):
    """Event when a completion is generated."""
    
    type: Literal["completion"] = "completion"
    completion_id: str
    language: str
    prompt: str
    segments: Optional[Segments] = None
    choices: List[Choice]
    user_agent: Optional[str] = None


class ChatCompletionEvent(Event):
    """Event when a chat completion is generated."""
    
    type: Literal["chat_completion"] = "chat_completion"


# Union type for all event types
EventUnion = ViewEvent | SelectEvent | DismissEvent | CompletionEvent | ChatCompletionEvent


class LogEntry(BaseModel):
    """A log entry with timestamp and user info."""
    
    user: Optional[str] = None
    ts: int  # Timestamp in milliseconds
    event: EventUnion


def timestamp() -> int:
    """Get current timestamp in milliseconds since epoch."""
    return int(time.time() * 1000)


class EventLogger(ABC):
    """Abstract base class for event loggers."""
    
    def log(self, user: Optional[str], event: Event):
        """
        Log an event with user and timestamp.
        
        Args:
            user: Optional user identifier
            event: Event to log
        """
        entry = LogEntry(
            user=user,
            ts=timestamp(),
            event=event
        )
        self.write(entry)
    
    @abstractmethod
    def write(self, entry: LogEntry):
        """
        Write a log entry.
        
        Args:
            entry: LogEntry to write
        """
        pass


class ComposedLogger(EventLogger):
    """Logger that writes to multiple loggers."""
    
    def __init__(self, logger1: EventLogger, logger2: EventLogger):
        """
        Initialize composed logger.
        
        Args:
            logger1: First logger
            logger2: Second logger
        """
        self.logger1 = logger1
        self.logger2 = logger2
    
    def write(self, entry: LogEntry):
        """Write to both loggers."""
        self.logger1.write(entry)
        self.logger2.write(entry)


class NoOpLogger(EventLogger):
    """Logger that does nothing (for testing/default)."""
    
    def write(self, entry: LogEntry):
        """Do nothing."""
        pass