"""
Health check endpoint.

GET /v1/health - Returns the health status of the server.
"""

from fastapi import APIRouter, Request
from typing import Optional

from tabby.services.health import HealthState, create_health_state


router = APIRouter(prefix="/v1", tags=["v1"])


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

async def health(request: Request):
    state = request.app.state.health_state
    config = request.app.state.config
    
    # 1. Force the status to 'ok'
    data = state.model_dump()
    data["status"] = "ok"
    
    # 2. FILL THE BRAIN: Tell the extension which model we are using
    # We check the completion config to find the name
    model_name = "tabby-python-model" # Fallback name
    
    if config.model.completion:
        if hasattr(config.model.completion, "model_id"):
            model_name = config.model.completion.model_id
        elif hasattr(config.model.completion, "model_name"):
            model_name = config.model.completion.model_name
            
    data["model"] = model_name
    
    # 3. Fill the models list
    data["models"] = {
        "completion": {
            "local": {
                "model_id": model_name,
                "device": data.get("device", "cpu"),
                "cuda_devices": data.get("cuda_devices", [])
            }
        },
        "chat": None, # Or a similar nested dict if you have a chat model
        "embedding": data.get("models", {}).get("embedding") 
    }
    
    return data