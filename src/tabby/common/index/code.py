"""
Field name constants for code indexing.

These constants define the field names used in the search index
for code documents and chunks.
"""

import re
from typing import List


# Maximum token length (tokens longer than this are filtered out)
MAX_TOKEN_LENGTH = 64


def tokenize_code(text: str) -> List[str]:
    """
    Tokenize code text into searchable terms.
    
    Extracts alphanumeric words (including underscores) and filters out:
    - Empty tokens
    - Tokens longer than 64 characters
    
    Args:
        text: Code text to tokenize
    
    Returns:
        List of token strings
    
    Examples:
        >>> tokenize_code("def hello_world(): pass")
        ['def', 'hello_world', 'pass']
        
        >>> tokenize_code("String fileName = file.getName();")
        ['String', 'fileName', 'file', 'getName']
    """
    # Extract words (alphanumeric + underscore sequences)
    tokens = re.findall(r'\w+', text)
    
    # Filter out tokens longer than MAX_TOKEN_LENGTH
    filtered_tokens = [
        token for token in tokens 
        if len(token) <= MAX_TOKEN_LENGTH
    ]
    
    return filtered_tokens


def tokenize_code_query(text: str) -> List[str]:
    """
    Tokenize a search query for code.
    
    Same as tokenize_code but optimized for query strings.
    
    Args:
        text: Query text to tokenize
    
    Returns:
        List of token strings
    """
    return tokenize_code(text)


class Fields:
    """Field name constants for code indexing."""
    
    # === Doc level fields ===
    # Commit ref of the file being indexed
    COMMIT = "commit"
    
    # === Chunk level fields ===
    CHUNK_GIT_URL = "chunk_git_url"
    CHUNK_FILEPATH = "chunk_filepath"
    CHUNK_LANGUAGE = "chunk_language"
    CHUNK_BODY = "chunk_body"
    
    # Optional, when None, it means this chunk contains entire content of the file
    CHUNK_START_LINE = "chunk_start_line"


def normalize_language(language: str) -> str:
    """
    Normalize language names for search.
    
    JavaScript/TypeScript variants are normalized to a common name.
    
    Args:
        language: Language identifier
    
    Returns:
        Normalized language name
    
    Examples:
        >>> normalize_language("javascript")
        'javascript-typescript'
        >>> normalize_language("typescript")
        'javascript-typescript'
        >>> normalize_language("python")
        'python'
    """
    if language in ("javascript", "typescript", "javascriptreact", "typescriptreact"):
        return "javascript-typescript"
    return language


__all__ = [
    "Fields", 
    "normalize_language", 
    "tokenize_code", 
    "tokenize_code_query", 
    "MAX_TOKEN_LENGTH"
]