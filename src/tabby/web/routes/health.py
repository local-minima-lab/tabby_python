"""
Health check endpoint.

GET /v1/health - Returns the health status of the server.
"""

from fastapi import APIRouter, Depends
from typing import Optional

from tabby.services.health import HealthState, create_health_state


router = APIRouter(prefix="/v1", tags=["v1"])


# Global health state (singleton)
_health_state: Optional[HealthState] = None


def get_health_state() -> HealthState:
    """Get the global health state."""
    global _health_state
    if _health_state is None:
        # Initialize with default values
        _health_state = create_health_state(device="cpu")
    return _health_state


def set_health_state(state: HealthState):
    """
    Set the global health state.
    
    This should be called during server startup with the actual
    device configuration.
    """
    global _health_state
    _health_state = state


@router.get(
    "/health",
    summary="Health check",
    description="Returns the health status of the Tabby server",
    response_model=HealthState,
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {
                        "model": "StarCoder-1B",
                        "device": "cpu",
                        "cuda_devices": [],
                        "models": {
                            "completion": {
                                "local": {
                                    "model_id": "StarCoder-1B",
                                    "device": "cpu",
                                    "cuda_devices": []
                                }
                            },
                            "embedding": {
                                "local": {
                                    "model_id": "Nomic-Embed-Text",
                                    "device": "cpu",
                                    "cuda_devices": []
                                }
                            }
                        },
                        "arch": "x86_64",
                        "cpu_info": "Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz",
                        "cpu_count": 12,
                        "version": {
                            "build_date": "2024-01-15",
                            "build_timestamp": "2024-01-15T10:30:00Z",
                            "git_sha": "abc123",
                            "git_describe": "0.30.0"
                        }
                    }
                }
            }
        }
    }
)
async def health(state: HealthState = Depends(get_health_state)) -> HealthState:
    """
    Get server health status.
    
    Returns comprehensive information about:
    - Loaded models (completion, chat, embedding)
    - Device information (CPU, CUDA)
    - System resources
    - Version information
    """
    return state