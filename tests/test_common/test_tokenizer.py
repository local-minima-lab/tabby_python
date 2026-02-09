# tests/test_common/test_tokenizer.py

import pytest
from tabby.common.index.code import tokenize_code, tokenize_code_query, MAX_TOKEN_LENGTH


def test_tokenize_code_basic():
    """Test basic code tokenization."""
    code = "def hello_world(): pass"
    tokens = tokenize_code(code)
    
    assert "def" in tokens
    assert "hello_world" in tokens
    assert "pass" in tokens


def test_tokenize_code_java():
    """Test tokenization of Java code (from Rust test)."""
    code = """public static String getFileExtension(String this_is_an_underscore_name) {
        String fileName = (new File(this_is_an_underscore_name)).getName();
        int dotIndex = fileName.lastIndexOf('.');
    }"""
    
    tokens = tokenize_code(code)
    
    expected = [
        "public",
        "static",
        "String",
        "getFileExtension",
        "String",
        "this_is_an_underscore_name",
        "String",
        "fileName",
        "new",
        "File",
        "this_is_an_underscore_name",
        "getName",
        "int",
        "dotIndex",
        "fileName",
        "lastIndexOf",
    ]
    
    assert tokens == expected


def test_tokenize_code_filters_long_tokens():
    """Test that tokens longer than 64 characters are filtered."""
    long_token = "a" * 100
    code = f"def {long_token}(): pass"
    
    tokens = tokenize_code(code)
    
    assert "def" in tokens
    assert "pass" in tokens
    assert long_token not in tokens  # Should be filtered out


def test_tokenize_code_empty_string():
    """Test tokenizing empty string."""
    tokens = tokenize_code("")
    assert tokens == []


def test_tokenize_code_preserves_underscores():
    """Test that underscores in identifiers are preserved."""
    code = "my_variable_name = get_value()"
    tokens = tokenize_code(code)
    
    assert "my_variable_name" in tokens
    assert "get_value" in tokens


def test_max_token_length_constant():
    """Test MAX_TOKEN_LENGTH constant."""
    assert MAX_TOKEN_LENGTH == 64


def test_tokenize_code_query():
    """Test query tokenization (same as code tokenization)."""
    query = "function getName"
    tokens = tokenize_code_query(query)
    
    assert "function" in tokens
    assert "getName" in tokens