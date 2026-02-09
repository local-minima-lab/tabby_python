import os
from pathlib import Path
from typing import Optional
import threading


class _TabbyRoot:
    """Thread-safe singleton for managing TABBY_ROOT path."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._path: Optional[Path] = None
        self._initialized = False
    
    def get(self) -> Path:
        """Get the TABBY_ROOT path."""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    # Check environment variable first
                    tabby_root_env = os.environ.get("TABBY_ROOT")
                    if tabby_root_env:
                        self._path = Path(tabby_root_env)
                    else:
                        # Fallback to home directory
                        self._path = Path.home() / ".tabby"
                    self._initialized = True
        
        return self._path
    
    def set(self, path: Path):
        """Set the TABBY_ROOT path (for testing)."""
        with self._lock:
            print(f"SET TABBY ROOT: '{path}'")
            self._path = path
            self._initialized = True


# Global instance
_TABBY_ROOT_INSTANCE = _TabbyRoot()

# Cache for TABBY_MODEL_CACHE_ROOT
_TABBY_MODEL_CACHE_ROOT: Optional[Path] = None
if "TABBY_MODEL_CACHE_ROOT" in os.environ:
    _TABBY_MODEL_CACHE_ROOT = Path(os.environ["TABBY_MODEL_CACHE_ROOT"])


def set_tabby_root(path: Path):
    """Set the TABBY_ROOT path (for testing purposes)."""
    _TABBY_ROOT_INSTANCE.set(path)


def tabby_root() -> Path:
    """Get the TABBY_ROOT directory path."""
    return _TABBY_ROOT_INSTANCE.get()


def config_file() -> Path:
    """Get the path to the config.toml file."""
    return tabby_root() / "config.toml"


def usage_id_file() -> Path:
    """Get the path to the usage anonymous ID file."""
    return tabby_root() / "usage_anonymous_id"


def repositories_dir() -> Path:
    """Get the path to the repositories directory."""
    return tabby_root() / "repositories"


def index_dir() -> Path:
    """Get the path to the index directory."""
    return tabby_root() / "index"


def models_dir() -> Path:
    """Get the path to the models directory."""
    if _TABBY_MODEL_CACHE_ROOT is not None:
        return _TABBY_MODEL_CACHE_ROOT
    else:
        return tabby_root() / "models"


def events_dir() -> Path:
    """Get the path to the events directory."""
    return tabby_root() / "events"