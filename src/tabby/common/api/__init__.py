"""
API definitions and types for Tabby.

Contains data structures and interfaces for various API operations.
"""

from .code import (
    CodeSearch,
    CodeSearchDocument,
    CodeSearchError,
    CodeSearchHit,
    CodeSearchParams,
    CodeSearchQuery,
    CodeSearchResponse,
    CodeSearchScores,
    IndexNotReadyError,
    QueryParserError,
    normalize_to_unix_path,
)

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

from .ingestion import (
    IngestionRequest,
    IngestionResponse,
    validate_ttl,
)

from .server_setting import (
    ServerSetting,
)

from .structured_doc import (
    DocSearch,
    DocSearchCommit,
    DocSearchDocument,
    DocSearchError,
    DocSearchHit,
    DocSearchIngestedDocument,
    DocSearchIssueDocument,
    DocSearchPageDocument,
    DocSearchPullDocument,
    DocSearchResponse,
    DocSearchWebDocument,
)

from .completion import (
    Choice,
    CompletionRequest,
    CompletionResponse,
    DebugData,
    DebugOptions,
    EditHistory,
    Segments,
    Snippet,
)

__all__ = [
    # Code search
    "CodeSearch",
    "CodeSearchDocument",
    "CodeSearchError",
    "CodeSearchHit",
    "CodeSearchParams",
    "CodeSearchQuery",
    "CodeSearchResponse",
    "CodeSearchScores",
    "IndexNotReadyError",
    "QueryParserError",
    "normalize_to_unix_path",
    
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
    
    # Ingestion
    "IngestionRequest",
    "IngestionResponse",
    "validate_ttl",
    
    # Server settings
    "ServerSetting",
    
    # Structured documents
    "DocSearch",
    "DocSearchCommit",
    "DocSearchDocument",
    "DocSearchError",
    "DocSearchHit",
    "DocSearchIngestedDocument",
    "DocSearchIssueDocument",
    "DocSearchPageDocument",
    "DocSearchPullDocument",
    "DocSearchResponse",
    "DocSearchWebDocument",

    # Completions
    "Choice",
    "CompletionRequest",
    "CompletionResponse",
    "DebugData",
    "DebugOptions",
    "EditHistory",
    "Segments",
    "Snippet",
]