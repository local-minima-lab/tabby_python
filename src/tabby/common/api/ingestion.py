"""
Document ingestion API types.

Defines request/response types for ingesting documents into the index.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


def validate_ttl(ttl: str) -> str:
    """
    Validate time-to-live duration string.
    
    Args:
        ttl: Duration string like "90d", "24h", "1w"
    
    Returns:
        The validated ttl string
    
    Raises:
        ValueError: If ttl format is invalid
    
    Examples:
        >>> validate_ttl("90d")
        '90d'
        >>> validate_ttl("24h")
        '24h'
        >>> validate_ttl("invalid")
        Traceback (most recent call last):
        ValueError: Invalid TTL format
    """
    # Common duration patterns: 90d, 24h, 1w, 30m, etc.
    # Matches: number + unit (d=days, h=hours, m=minutes, s=seconds, w=weeks)
    pattern = r'^\d+[dhmsw]$'
    
    if not re.match(pattern, ttl.lower()):
        raise ValueError(f"Invalid TTL format: {ttl}. Expected format like '90d', '24h', '1w'")
    
    return ttl


class IngestionRequest(BaseModel):
    """
    Request to ingest a document into the index.
    
    Documents are indexed for code search and RAG functionality.
    """
    
    # Source of the document (frontend available, backend sourceId: `ingestedSource:${source}`)
    source: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Source identifier for the document"
    )
    
    # Unique within the same source
    id: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Unique identifier for the document within its source"
    )
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=65535,
        description="Document title"
    )
    
    body: str = Field(
        ...,
        description="Document body/content"
    )
    
    link: Optional[str] = Field(
        None,
        description="Optional link to the original document"
    )
    
    # Time-to-live duration (optional). Duration string like "90d"
    ttl: Optional[str] = Field(
        None,
        description="Time-to-live duration (e.g., '90d', '24h', '1w')"
    )
    
    @field_validator('ttl')
    @classmethod
    def validate_ttl_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate TTL format if provided."""
        if v is not None:
            return validate_ttl(v)
        return v


class IngestionResponse(BaseModel):
    """Response after ingesting a document."""
    
    id: str = Field(..., description="Document ID")
    source: str = Field(..., description="Source identifier")
    message: str = Field(..., description="Status message")