import pytest
from tabby.common import languages


def test_get_language_python():
    """Test getting Python language."""
    python = languages.get_language("python")
    
    assert python.language() == "python"
    assert "py" in python.exts
    assert python.line_comment == "#"
    assert "def" in python.top_level_keywords


def test_get_language_by_ext():
    """Test getting language by extension."""
    python = languages.get_language_by_ext("py")
    assert python.language() == "python"
    
    python = languages.get_language_by_ext(".py")
    assert python.language() == "python"


def test_get_language_unknown():
    """Test unknown language returns UNKNOWN_LANGUAGE."""
    unknown = languages.get_language("nonexistent")
    assert unknown.language() == "unknown"


def test_language_stop_words():
    """Test stop word generation."""
    python = languages.get_language("python")
    stop_words = python.get_stop_words()
    
    # Check defaults
    assert "\n\n" in stop_words
    assert "<fim_prefix>" in stop_words
    
    # Check language-specific
    assert "\n#" in stop_words
    assert "\ndef" in stop_words
    assert "\nclass" in stop_words


def test_javascript_typescript_aliases():
    """Test JavaScript/TypeScript language aliases."""
    js = languages.get_language("javascript")
    ts = languages.get_language("typescript")
    jsx = languages.get_language("javascriptreact")
    
    # All should return same config
    assert js == ts == jsx