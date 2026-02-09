"""
Structured document search API types.

Defines document types for different kinds of searchable content
(web pages, GitHub issues, PRs, commits, ingested documents, etc.).
"""

from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class DocSearchError(Exception):
    """Base exception for document search errors."""
    pass


class IndexNotReadyError(DocSearchError):
    """Raised when the search index is not ready."""
    
    def __init__(self):
        super().__init__("index not ready")


class QueryParserError(DocSearchError):
    """Raised when query parsing fails."""
    pass


class DocSearchWebDocument(BaseModel):
    """Web page document."""
    
    title: str
    link: str
    snippet: str


class DocSearchIssueDocument(BaseModel):
    """GitHub issue document."""
    
    title: str
    link: str
    author_email: Optional[str] = None
    body: str
    closed: bool


class DocSearchPullDocument(BaseModel):
    """GitHub pull request document."""
    
    title: str
    link: str
    author_email: Optional[str] = None
    body: str
    diff: str
    merged: bool


class DocSearchCommit(BaseModel):
    """Git commit document."""
    
    sha: str
    message: str
    author_email: str
    author_at: datetime


class DocSearchPageDocument(BaseModel):
    """Documentation page document."""
    
    link: str
    title: str
    content: str


class DocSearchIngestedDocument(BaseModel):
    """User-ingested document."""
    
    id: str
    title: str
    body: str
    link: Optional[str] = None


# Union type for all document types
DocSearchDocument = Union[
    DocSearchWebDocument,
    DocSearchIssueDocument,
    DocSearchPullDocument,
    DocSearchCommit,
    DocSearchPageDocument,
    DocSearchIngestedDocument,
]


class DocSearchHit(BaseModel):
    """A single document search result."""
    
    score: float
    doc: DocSearchDocument
    
    class Config:
        # Allow union types
        arbitrary_types_allowed = True


class DocSearchResponse(BaseModel):
    """Response from a document search query."""
    
    hits: List[DocSearchHit] = Field(default_factory=list)


# Abstract base class for document search implementations
from abc import ABC, abstractmethod


class DocSearch(ABC):
    """Abstract interface for document search implementations."""
    
    @abstractmethod
    async def search(
        self,
        source_ids: List[str],
        q: str,
        limit: int,
    ) -> DocSearchResponse:
        """
        Search documents from underlying index.
        
        Args:
            source_ids: Filter documents by source IDs. When empty, search all sources.
            q: Search query string
            limit: Maximum number of results to return
        
        Returns:
            DocSearchResponse with matching documents
        
        Raises:
            DocSearchError: If search fails
        """
        pass