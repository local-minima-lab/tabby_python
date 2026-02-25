"""
Health service - System and model health information.

This module handles health state creation and system info gathering.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
import platform
import psutil
import os
from datetime import datetime

from tabby.common.config import Config, ModelConfig, HttpModelConfig, LocalModelConfig, ModelConfigGroup


class Version(BaseModel):
    """Version information."""
    build_date: str
    build_timestamp: str
    git_sha: str
    git_describe: str


class RemoteModelHealth(BaseModel):
    """Health info for remote (HTTP) models."""
    kind: str
    model_name: Optional[str] = None
    api_endpoint: str


class LocalModelHealth(BaseModel):
    """Health info for local models."""
    model_id: str
    device: str
    cuda_devices: List[str] = Field(default_factory=list)


class ModelsHealth(BaseModel):
    """Health status for all models."""
    completion: Optional[dict] = None
    chat: Optional[dict] = None
    embedding: dict


class HealthState(BaseModel):
    """Complete health state of the server."""
    status: str = "ok"
    # Legacy fields (deprecated but still returned)
    model: Optional[str] = None
    chat_model: Optional[str] = None
    chat_device: Optional[str] = None
    device: str
    cuda_devices: List[str] = Field(default_factory=list)
    
    # Current model health
    models: ModelsHealth
    
    # CPU information
    arch: str
    cpu_info: str
    cpu_count: int
    
    # Version info
    version: Version
    
    # Webserver status
    webserver: Optional[bool] = None


def read_cpu_info() -> tuple[str, int]:
    """Read CPU information."""
    try:
        cpu_count = psutil.cpu_count(logical=True)
        
        # Get CPU brand info
        if platform.system() == "Darwin":  # macOS
            import subprocess
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True
            )
            cpu_info = result.stdout.strip() if result.returncode == 0 else platform.processor()
        elif platform.system() == "Linux":
            try:
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            cpu_info = line.split(":")[1].strip()
                            break
                    else:
                        cpu_info = platform.processor()
            except:
                cpu_info = platform.processor()
        else:  # Windows or other
            cpu_info = platform.processor()
        
        return cpu_info or "unknown", cpu_count or 0
    except:
        return "unknown", 0


def read_cuda_devices() -> List[str]:
    """Read CUDA device information."""
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        devices = []
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            devices.append(name)
        pynvml.nvmlShutdown()
        return devices
    except:
        return []


def model_config_to_health(
    model_config: Optional[ModelConfig], 
    device: str, 
    cuda_devices: List[str]
) -> Optional[dict]:
    """Convert ModelConfig to health dict."""
    if model_config is None:
        return None
    
    if isinstance(model_config, HttpModelConfig):
        return {
            "remote": {
                "kind": model_config.kind,
                "model_name": model_config.model_name,
                "api_endpoint": model_config.api_endpoint or "",
            }
        }
    elif isinstance(model_config, LocalModelConfig):
        return {
            "local": {
                "model_id": model_config.model_id,
                "device": device,
                "cuda_devices": cuda_devices,
            }
        }
    return None


def get_model_name(model_config: Optional[ModelConfig]) -> Optional[str]:
    """Get display name for a model."""
    if model_config is None:
        return None
    
    if isinstance(model_config, HttpModelConfig):
        return model_config.model_name or "Remote"
    elif isinstance(model_config, LocalModelConfig):
        return model_config.model_id
    return None


def create_version() -> Version:
    """Create version information."""
    return Version(
        build_date=os.environ.get("VERGEN_BUILD_DATE", datetime.now().strftime("%Y-%m-%d")),
        build_timestamp=os.environ.get("VERGEN_BUILD_TIMESTAMP", datetime.now().isoformat()),
        git_sha=os.environ.get("VERGEN_GIT_SHA", "dev"),
        git_describe=os.environ.get("VERGEN_GIT_DESCRIBE", "0.30.0-dev"),
    )


def create_health_state(
    model_config: Optional[ModelConfigGroup] = None,
    device: str = "cpu",
    chat_device: Optional[str] = None,
    webserver: Optional[bool] = None,
) -> HealthState:
    """
    Create a HealthState instance.
    
    Args:
        model_config: Model configuration (if None, loads from config file)
        device: Device for completion/embedding models
        chat_device: Device for chat model (defaults to same as device)
        webserver: Whether webserver is enabled
    
    Returns:
        HealthState with all system and model information
    """
    # Load config if not provided
    if model_config is None:
        try:
            config = Config.load()
            model_config = config.model
        except:
            model_config = ModelConfigGroup()
    
    # Read system info
    cpu_info, cpu_count = read_cpu_info()
    cuda_devices = read_cuda_devices()
    
    # Build models health
    completion_health = model_config_to_health(
        model_config.completion, device, cuda_devices
    )
    chat_health = model_config_to_health(
        model_config.chat, chat_device or device, cuda_devices
    )
    embedding_health = model_config_to_health(
        model_config.embedding, device, cuda_devices
    )
    
    models = ModelsHealth(
        completion=completion_health,
        chat=chat_health,
        embedding=embedding_health or {
            "local": {
                "model_id": "Nomic-Embed-Text",
                "device": device,
                "cuda_devices": cuda_devices
            }
        },
    )
    
    return HealthState(
        # Legacy fields
        model=get_model_name(model_config.completion),
        chat_model=get_model_name(model_config.chat),
        chat_device=chat_device,
        device=device,
        cuda_devices=cuda_devices,
        
        # Current fields
        models=models,
        arch=platform.machine(),
        cpu_info=cpu_info,
        cpu_count=cpu_count,
        version=create_version(),
        webserver=webserver,
    )