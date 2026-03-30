"""
API definitions and types for Tabby.

Contains data structures and interfaces for various API operations.
"""
from .event import (
    Choice,
    ChatCompletionEvent,
    CompletionEvent,
    ComposedLogger,
    Declaration,
    DismissEvent,
    Event,
    EventLogger,
    EventUnion,
    LogEntry,
    LogEventRequest,
    Message,
    NoOpLogger,
    Segments,
    SelectEvent,
    SelectKind,
    ViewEvent,
    timestamp,
)

from .server_setting import (
    ServerSetting,
)

__all__ = [
    # Events
    "Choice",
    "ChatCompletionEvent",
    "CompletionEvent",
    "ComposedLogger",
    "Declaration",
    "DismissEvent",
    "Event",
    "EventLogger",
    "EventUnion",
    "LogEntry",
    "LogEventRequest",
    "Message",
    "NoOpLogger",
    "Segments",
    "SelectEvent",
    "SelectKind",
    "ViewEvent",
    "timestamp",
    
    
    # Server settings
    "ServerSetting",
]