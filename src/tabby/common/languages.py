import os
from pathlib import Path
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import tomllib as tomli 

# Global default stop words
DEFAULT_STOP_WORDS = [
    "\n\n",
    "\n\n  ",
    "\n\n    ",
    "\n\n      ",
    "\n\n        ",
    "\n\n          ",
    "\n\n            ",
    "\n\n              ",
    "\n\n\t",
    "\n\n\t\t",
    "\n\n\t\t\t",
    "\n\n\t\t\t\t",
    "\n\n\t\t\t\t\t",
    "\n\n\t\t\t\t\t\t",
    "\n\n\t\t\t\t\t\t\t",
    # FIXME: Hack for codellama / codegemma to simplify tabby's implementation.
    # StarCoder
    "<fim_prefix>",
    "<fim_suffix>",
    "<fim_middle>",
    "<file_sep>",
    # CodeLlama
    " <EOT>",
    # CodeGemma
    "<|fim_prefix|>",
    "<|fim_suffix|>",
    "<|fim_middle|>",
    "<|file_separator|>",
    # chat_ml
    "<|system|>",
    "<|user|>",
    "<|end|>",
    "<|assistant|>",
]


class Language(BaseModel):
    """Represents a programming language configuration."""
    
    languages: List[str]
    exts: List[str]
    top_level_keywords: Optional[List[str]] = None
    line_comment: Optional[str] = None
    chunk_size: Optional[int] = None

    def get_stop_words(self) -> List[str]:
        """Generate stop words for this language."""
        out = DEFAULT_STOP_WORDS.copy()

        if self.line_comment:
            out.append(f"\n{self.line_comment}")

        if self.top_level_keywords:
            for word in self.top_level_keywords:
                out.append(f"\n{word}")

        return out

    def language(self) -> str:
        """Return the primary language name."""
        return self.languages[0]


class ConfigList(BaseModel):
    """Container for language configurations."""
    
    config: List[Language] = Field(default_factory=list)


# Singleton for unknown language
UNKNOWN_LANGUAGE = Language(
    languages=["unknown"],
    line_comment="",
    top_level_keywords=[],
    exts=[],
    chunk_size=None
)


class LanguageRegistry:
    """Manages language configurations and lookups."""
    
    def __init__(self):
        self._config: ConfigList = None
        self._language_config_mapping: Dict[str, Language] = None
        self._exts_language_mapping: Dict[str, str] = None
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of language configurations."""
        if self._initialized:
            return

        # Load the base configuration from TOML file
        config_list = self._load_languages_toml()
        
        # Load additional languages from config if available
        try:
            from . import config  # Adjust import based on your structure
            user_config = config.Config.load()
            if user_config and hasattr(user_config, 'additional_languages'):
                config_list.config.extend(user_config.additional_languages)
        except (ImportError, Exception):
            # If config module doesn't exist or fails, just use base config
            pass

        self._config = config_list
        self._build_mappings()
        self._initialized = True

    def _load_languages_toml(self) -> ConfigList:
        """Load language configurations from TOML file."""
        # Adjust path to point to your assets/languages.toml file
        toml_path = Path(__file__).parent / "assets" / "languages.toml"
        
        if not toml_path.exists():
            # Return empty config if file doesn't exist
            return ConfigList(config=[])
        
        with open(toml_path, "rb") as f:
            data = tomli.load(f)
        
        # Parse TOML data into Language objects
        # The TOML uses [[config]] arrays
        languages = []
        if "config" in data:
            for lang_data in data["config"]:
                languages.append(Language(**lang_data))
        
        return ConfigList(config=languages)

    def _build_mappings(self):
        """Build lookup mappings for languages and extensions."""
        self._language_config_mapping = {}
        self._exts_language_mapping = {}

        for lang_config in self._config.config:
            # Map language names to config
            for lang_name in lang_config.languages:
                if lang_name in self._language_config_mapping:
                    raise ValueError(f"Duplicate language found: {lang_name}")
                self._language_config_mapping[lang_name] = lang_config

            # Map file extensions to primary language name
            primary_lang = lang_config.language()
            for ext in lang_config.exts:
                if ext in self._exts_language_mapping:
                    raise ValueError(f"Duplicate extension found: {ext}")
                self._exts_language_mapping[ext] = primary_lang

    def get_language(self, language: str) -> Language:
        """Get language configuration by language name."""
        self._initialize()
        return self._language_config_mapping.get(language, UNKNOWN_LANGUAGE)

    def get_language_by_ext(self, ext: str) -> Optional[Language]:
        """Get language configuration by file extension."""
        self._initialize()
        
        # Handle Path objects or strings
        if isinstance(ext, (Path, os.PathLike)):
            ext = Path(ext).suffix.lstrip('.')
        elif ext.startswith('.'):
            ext = ext[1:]
        
        if not ext:
            return None
            
        primary_lang = self._exts_language_mapping.get(ext)
        if primary_lang:
            return self.get_language(primary_lang)
        return None


# Global registry instance (lazy-initialized)
_registry = LanguageRegistry()


# Public API functions
def get_language(language: str) -> Language:
    """Get language configuration by language name."""
    return _registry.get_language(language)


def get_language_by_ext(ext: str) -> Optional[Language]:
    """Get language configuration by file extension."""
    return _registry.get_language_by_ext(ext)