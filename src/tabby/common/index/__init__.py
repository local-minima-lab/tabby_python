"""
Index-related types and utilities for Tabby.

Contains field names, corpus identifiers, and index schema constants.

Note: The actual index implementation will be in tabby.index module.
This module only contains shared constants and types.
"""

# Field name constants
FIELD_SOURCE_ID = "source_id"
FIELD_ATTRIBUTES = "attributes"
FIELD_CHUNK_ID = "chunk_id"
FIELD_UPDATED_AT = "updated_at"
FIELD_FAILED_CHUNKS_COUNT = "failed_chunks_count"


class CorpusType:
    """
    Corpus type identifiers.
    
    A corpus is a group of documents with a consistent schema.
    """
    CODE = "code"
    STRUCTURED_DOC = "structured_doc"


# Lazy import to avoid circular imports
def __getattr__(name):
    """Lazy loading of submodules to avoid circular imports."""
    if name == "code":
        from . import code as _code
        return _code
    elif name == "structured_doc":
        from . import structured_doc as _structured_doc
        return _structured_doc
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Submodules (lazily loaded)
    "code",
    "structured_doc",
    
    # Constants
    "FIELD_SOURCE_ID",
    "FIELD_ATTRIBUTES",
    "FIELD_CHUNK_ID",
    "FIELD_UPDATED_AT",
    "FIELD_FAILED_CHUNKS_COUNT",
    "CorpusType",
]