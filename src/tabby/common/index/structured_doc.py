"""
Field name constants for structured document indexing.

These constants define the field names used in the search index
for different document types (web, issues, PRs, commits, pages, etc.).
"""


class Fields:
    """Field name constants for structured documents."""
    
    KIND = "kind"
    
    class Web:
        """Web document fields."""
        TITLE = "title"
        LINK = "link"
        CHUNK_TEXT = "chunk_text"
    
    class Issue:
        """GitHub issue fields."""
        TITLE = "title"
        LINK = "link"
        AUTHOR_EMAIL = "author_email"
        BODY = "body"
        CLOSED = "closed"
    
    class Pull:
        """GitHub pull request fields."""
        TITLE = "title"
        LINK = "link"
        AUTHOR_EMAIL = "author_email"
        BODY = "body"
        DIFF = "diff"
        MERGED = "merged"
    
    class Commit:
        """Git commit fields (doc level)."""
        SHA = "sha"
        MESSAGE = "message"
        AUTHOR_EMAIL = "author_email"
        AUTHOR_AT = "author_at"
    
    class Page:
        """Documentation page fields."""
        # Doc level fields
        LINK = "link"
        TITLE = "title"
        
        # Chunk level fields
        CHUNK_CONTENT = "chunk_text"
    
    class Ingested:
        """User-ingested document fields."""
        # Doc level fields
        TITLE = "title"
        LINK = "link"
        
        # Chunk level fields
        CHUNK_BODY = "chunk_body"


__all__ = ["Fields"]