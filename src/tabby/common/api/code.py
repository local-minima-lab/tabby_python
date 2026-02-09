"""
Code search API types and interfaces.

Defines data structures and interfaces for code search functionality.
"""

from typing import List, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from enum import Enum


class CodeSearchScores(BaseModel):
    """Scores for a code search result."""
    
    # Reciprocal rank fusion score: https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html
    rrf: float = 0.0
    bm25: float = 0.0
    embedding: float = 0.0


class CodeSearchDocument(BaseModel):
    """A document returned from code search."""
    
    # Unique identifier for the file in the repository, stringified SourceFileKey
    file_id: str = ""
    chunk_id: str = ""
    
    body: str = ""
    filepath: str = ""
    git_url: str = ""
    
    # commit represents the specific revision at which the file was last edited
    # FIXME(kweizh): This should be a required field after 0.25.0.
    commit: Optional[str] = None
    
    language: str = ""
    
    # When start_line is None, it represents the entire file
    start_line: Optional[int] = None


class CodeSearchHit(BaseModel):
    """A single search result hit."""
    
    scores: CodeSearchScores = Field(default_factory=CodeSearchScores)
    doc: CodeSearchDocument = Field(default_factory=CodeSearchDocument)


class CodeSearchResponse(BaseModel):
    """Response from a code search query."""
    
    hits: List[CodeSearchHit] = Field(default_factory=list)


class CodeSearchError(Exception):
    """Base exception for code search errors."""
    pass


class IndexNotReadyError(CodeSearchError):
    """Raised when the search index is not ready."""
    
    def __init__(self):
        super().__init__("index not ready")


class QueryParserError(CodeSearchError):
    """Raised when query parsing fails."""
    pass


class CodeSearchQuery(BaseModel):
    """Query parameters for code search."""
    
    # filepath in code search query always normalize to unix style
    filepath: Optional[str] = None
    language: Optional[str] = None
    content: str
    source_id: str
    
    def __init__(self, **data):
        """Initialize and normalize filepath to Unix style."""
        if 'filepath' in data and data['filepath'] is not None:
            data['filepath'] = normalize_to_unix_path(data['filepath'])
        super().__init__(**data)


class CodeSearchParams(BaseModel):
    """Parameters controlling code search behavior."""
    
    min_embedding_score: float = 0.75
    min_bm25_score: float = 8.0
    min_rrf_score: float = 0.028
    
    # At most num_to_return results will be returned
    num_to_return: int = 20
    
    # At most num_to_score results will be scored
    num_to_score: int = 40


class CodeSearch(ABC):
    """Abstract interface for code search implementations."""
    
    @abstractmethod
    async def search_in_language(
        self,
        query: CodeSearchQuery,
        params: CodeSearchParams,
    ) -> CodeSearchResponse:
        """
        Search for code in a specific language.
        
        Args:
            query: Search query parameters
            params: Search configuration parameters
        
        Returns:
            CodeSearchResponse with matching results
        
        Raises:
            CodeSearchError: If search fails
        """
        pass


def normalize_to_unix_path(filepath: str) -> str:
    """
    Normalize the path from different platforms to unix style path.
    
    Args:
        filepath: Path string (can be Windows or Unix style)
    
    Returns:
        Unix-style path with forward slashes
    
    Examples:
        >>> normalize_to_unix_path("src\\test\\file.txt")
        'src/test/file.txt'
        >>> normalize_to_unix_path("./src/main.rs")
        './src/main.rs'
    """
    return filepath.replace('\\', '/')