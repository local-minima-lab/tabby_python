"""
Common tabby types and utilities.

Defines common types and utilities used across multiple tabby subprojects, 
especially serialization and deserialization targets.
"""

# Import all submodules
from . import config
from . import constants
from . import languages
from . import path
from . import registry
from . import terminal
from . import usage

# api and index are subdirectories with their own __init__.py
from . import api
from . import index

# Re-export commonly used API types
from .api.code import (
    CodeSearchParams,
    CodeSearchQuery,
    CodeSearchResponse,
)

from .api.event import (
    Event,
    EventLogger,
    CompletionEvent,
    ChatCompletionEvent,
)

# Note: axum is Rust's web framework, not needed in Python
# We'll use FastAPI/Flask instead at a higher level

# Re-export commonly used items for convenience
# This allows: from tabby.common import Config, get_language
from .config import (
    Config,
    RepositoryConfig,
    ServerConfig,
    ModelConfig,
    HttpModelConfig,
    LocalModelConfig,
    ModelConfigGroup,
    CompletionConfig,
    EmbeddingConfig,
    AnswerConfig,
    CodeRepository,
    PageConfig,
    config_index_to_id,
    config_id_to_index,
)

from .constants import (
    USER_HEADER_FIELD_NAME,
)

from .terminal import (
    HeaderFormat,
    InfoMessage,
)

from .usage import (
    capture,
    capture_sync,
    cleanup as usage_cleanup,
)

from .registry import (
    ModelInfo,
    ModelRegistry,
    PartitionModelUrl,
    parse_model_id,
    LEGACY_GGML_MODEL_PATH,
    GGML_MODEL_PARTITIONED_PREFIX,
)

from .languages import (
    Language,
    ConfigList,
    UNKNOWN_LANGUAGE,
    get_language,
    get_language_by_ext,
    DEFAULT_STOP_WORDS,
)

from .path import (
    tabby_root,
    config_file,
    usage_id_file,
    repositories_dir,
    index_dir,
    models_dir,
    events_dir,
    set_tabby_root,
)

# When other modules are converted, import them here:
# from .constants import ...
# from .registry import ...
# from .terminal import ...
# from .usage import ...

__all__ = [
    # Submodules
    "api",
    "config",
    "constants",
    "index",
    "languages",
    "path",
    "registry",
    "terminal",
    "usage",
    
    # Config classes and functions
    "Config",
    "RepositoryConfig",
    "ServerConfig",
    "ModelConfig",
    "HttpModelConfig",
    "LocalModelConfig",
    "ModelConfigGroup",
    "CompletionConfig",
    "EmbeddingConfig",
    "AnswerConfig",
    "CodeRepository",
    "PageConfig",
    "config_index_to_id",
    "config_id_to_index",
    
    # Language classes and functions
    "Language",
    "ConfigList",
    "UNKNOWN_LANGUAGE",
    "get_language",
    "get_language_by_ext",
    "DEFAULT_STOP_WORDS",
    
    # Path functions
    "tabby_root",
    "config_file",
    "usage_id_file",
    "repositories_dir",
    "index_dir",
    "models_dir",
    "events_dir",
    "set_tabby_root",
    
    # Constants
    "USER_HEADER_FIELD_NAME",
    
    # Terminal formatting
    "HeaderFormat",
    "InfoMessage",
    
    # Usage tracking
    "capture",
    "capture_sync",
    "usage_cleanup",
    
    # Model registry
    "ModelInfo",
    "ModelRegistry",
    "PartitionModelUrl",
    "parse_model_id",
    "LEGACY_GGML_MODEL_PATH",
    "GGML_MODEL_PARTITIONED_PREFIX",
    
    # API types
    "CodeSearchParams",
    "CodeSearchQuery",
    "CodeSearchResponse",
    "Event",
    "EventLogger",
    "CompletionEvent",
    "ChatCompletionEvent",
]