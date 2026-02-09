"""
Model registry management for Tabby.

Handles downloading, caching, and managing model metadata from remote registries.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Tuple
import asyncio

try:
    import httpx
except ImportError:
    httpx = None

from pydantic import BaseModel, Field

from . import path as path_module


# Legacy model path constants
LEGACY_GGML_MODEL_PATH = f"ggml{os.sep}model.gguf"
GGML_MODEL_PARTITIONED_PREFIX = "model-00001-of-"


class PartitionModelUrl(BaseModel):
    """URL and checksum for a model partition."""
    
    urls: List[str]
    sha256: str


class ModelInfo(BaseModel):
    """Information about a model in the registry."""
    
    name: str
    prompt_template: Optional[str] = None
    chat_template: Optional[str] = None
    urls: Optional[List[str]] = None
    sha256: Optional[str] = None
    partition_urls: Optional[List[PartitionModelUrl]] = None


def models_json_file(registry: str) -> Path:
    """Get path to the models.json file for a registry."""
    return path_module.models_dir() / registry / "models.json"


async def load_remote_registry(registry: str) -> List[ModelInfo]:
    """
    Load model registry from remote GitHub repository.
    
    Args:
        registry: Registry name (e.g., "TabbyML")
    
    Returns:
        List of ModelInfo objects
    
    Raises:
        Exception: If download or parsing fails
    """
    if not httpx:
        raise ImportError("httpx is required for loading remote registry")
    
    # Create HTTP client with timeout
    async with httpx.AsyncClient(timeout=5.0) as client:
        url = f"https://raw.githubusercontent.com/{registry}/registry-tabby/main/models.json"
        
        response = await client.get(url)
        response.raise_for_status()
        
        model_data = response.json()
        
        # Cache the registry locally
        registry_dir = path_module.models_dir() / registry
        registry_dir.mkdir(parents=True, exist_ok=True)
        
        with open(models_json_file(registry), 'w') as f:
            json.dump(model_data, f, indent=2)
        
        # Parse into ModelInfo objects
        return [ModelInfo(**model) for model in model_data]


def load_local_registry(registry: str) -> List[ModelInfo]:
    """
    Load model registry from local cache.
    
    Args:
        registry: Registry name (e.g., "TabbyML")
    
    Returns:
        List of ModelInfo objects
    
    Raises:
        FileNotFoundError: If local registry doesn't exist
    """
    registry_file = models_json_file(registry)
    
    if not registry_file.exists():
        raise FileNotFoundError(f"Local registry not found: {registry_file}")
    
    with open(registry_file, 'r') as f:
        model_data = json.load(f)
    
    return [ModelInfo(**model) for model in model_data]


class ModelRegistry:
    """
    Manages models from a registry (e.g., TabbyML).
    
    Directory structure:
        ~/.tabby/models/{registry}/
            models.json              # Registry metadata
            {model_name}/
                tabby.json           # Model info
                ggml/                # Model files
                    model-00001-of-00001.gguf  # Model file(s)
    """
    
    def __init__(self, name: str, models: List[ModelInfo]):
        """
        Initialize a model registry.
        
        Args:
            name: Registry name (e.g., "TabbyML")
            models: List of available models
        """
        self.name = name
        self.models = models
    
    @classmethod
    async def new(cls, registry: str) -> 'ModelRegistry':
        """
        Create a new ModelRegistry, fetching from remote or loading from cache.
        
        Args:
            registry: Registry name (e.g., "TabbyML")
        
        Returns:
            ModelRegistry instance
        """
        try:
            # Try remote first
            models = await load_remote_registry(registry)
        except Exception as remote_err:
            # Fall back to local cache
            try:
                models = load_local_registry(registry)
            except Exception:
                raise RuntimeError(
                    f"Failed to fetch model organization <{registry}>: {remote_err}"
                )
        
        return cls(registry, models)
    
    def get_model_store_dir(self, name: str) -> Path:
        """
        Get the storage directory for a model's files.
        
        Args:
            name: Model name
        
        Returns:
            Path like ~/.tabby/models/TabbyML/StarCoder-1B/ggml
        """
        return self.get_model_dir(name) / "ggml"
    
    def get_model_dir(self, name: str) -> Path:
        """
        Get the root directory for a model.
        
        Args:
            name: Model name
        
        Returns:
            Path like ~/.tabby/models/TabbyML/StarCoder-1B
        """
        return path_module.models_dir() / self.name / name
    
    def get_model_entry_path(self, name: str) -> Optional[Path]:
        """
        Get the entrypoint model file (first partition).
        
        Looks for files with prefix "model-00001-of-"
        
        Args:
            name: Model name
        
        Returns:
            Path to model file, or None if not found
        """
        store_dir = self.get_model_store_dir(name)
        
        if not store_dir.exists():
            return None
        
        for entry in store_dir.iterdir():
            if entry.name.startswith(GGML_MODEL_PARTITIONED_PREFIX):
                return entry
        
        return None
    
    def migrate_legacy_model_path(self, name: str) -> None:
        """
        Migrate old model path format to new format.
        
        Old: ~/.tabby/models/TabbyML/StarCoder-1B/ggml/model.gguf
        New: ~/.tabby/models/TabbyML/StarCoder-1B/ggml/model-00001-of-00001.gguf
        
        Args:
            name: Model name
        """
        old_model_path = self.get_model_dir(name) / LEGACY_GGML_MODEL_PATH
        
        if old_model_path.exists():
            self.migrate_model_path(name, old_model_path)
    
    def get_model_path(self, name: str) -> Path:
        """
        Get the legacy model path.
        
        Args:
            name: Model name
        
        Returns:
            Path to model file (legacy format)
        """
        return self.get_model_dir(name) / LEGACY_GGML_MODEL_PATH
    
    def migrate_model_path(self, name: str, old_model_path: Path) -> None:
        """
        Migrate a model from old path to new path.
        
        Args:
            name: Model name
            old_model_path: Old model file path
        """
        # Legacy model always has a single file
        new_model_path = self.get_model_store_dir(name) / "model-00001-of-00001.gguf"
        
        # Create directory if needed
        new_model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rename/move the file
        old_model_path.rename(new_model_path)
    
    def save_model_info(self, name: str) -> None:
        """
        Save model metadata to tabby.json.
        
        Args:
            name: Model name
        """
        model_info = self.get_model_info(name)
        model_dir = self.get_model_dir(name)
        info_path = model_dir / "tabby.json"
        
        # Create directory if needed
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        with open(info_path, 'w') as f:
            json.dump(model_info.model_dump(exclude_none=True), f, indent=2)
    
    def get_model_info(self, name: str) -> ModelInfo:
        """
        Get metadata for a specific model.
        
        Args:
            name: Model name
        
        Returns:
            ModelInfo object
        
        Raises:
            ValueError: If model not found in registry
        """
        for model in self.models:
            if model.name == name:
                return model
        
        raise ValueError(
            f"Invalid `model_id` <{self.name}/{name}>; please consult "
            f"https://github.com/{self.name}/registry-tabby for the correct `model_id`."
        )


def parse_model_id(model_id: str) -> Tuple[str, str]:
    """
    Parse a model ID into registry and model name.
    
    Args:
        model_id: Model ID like "TabbyML/StarCoder-1B" or just "StarCoder-1B"
    
    Returns:
        Tuple of (registry, model_name)
        If no registry specified, defaults to "TabbyML"
    
    Examples:
        >>> parse_model_id("StarCoder-1B")
        ("TabbyML", "StarCoder-1B")
        >>> parse_model_id("TabbyML/StarCoder-1B")
        ("TabbyML", "StarCoder-1B")
    
    Raises:
        ValueError: If model_id format is invalid
    """
    parts = model_id.split('/')
    
    if len(parts) == 1:
        return ("TabbyML", parts[0])
    elif len(parts) == 2:
        return (parts[0], parts[1])
    else:
        raise ValueError(f"Invalid model id {model_id}")