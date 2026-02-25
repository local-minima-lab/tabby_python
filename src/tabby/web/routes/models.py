from typing import Optional, List
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from tabby.common.config import Config, HttpModelConfig

router = APIRouter(prefix="/v1beta", tags=["v1beta"])


class ModelInfo(BaseModel):
    """Information about available models."""
    
    completion: Optional[List[str]] = Field(
        default=None,
        description="Available completion models"
    )
    chat: Optional[List[str]] = Field(
        default=None,
        description="Available chat models"
    )

    @staticmethod
    def from_config(config: Config) -> 'ModelInfo':
        completion_models = []
        chat_models = []
        
        # 1. Handle Completion Models
        if config.model.completion:
            if hasattr(config.model.completion, "model_id"): # Local model
                completion_models.append(config.model.completion.model_id)
            elif hasattr(config.model.completion, "model_name"): # HTTP model
                completion_models.append(config.model.completion.model_name)

        # 2. Handle Chat Models
        if config.model.chat:
            if hasattr(config.model.chat, "model_id"):
                chat_models.append(config.model.chat.model_id)
                
        return ModelInfo(
            completion=completion_models if completion_models else ["tabby-default"],
            chat=chat_models if chat_models else ["tabby-chat-default"]
        )


@router.get(
    "/models",
    response_model=ModelInfo,
    summary="Get available models",
    operation_id="models",
    responses={
        200: {"description": "Success"}
    }
)
async def get_models(request: Request) -> ModelInfo:
    """
    Get information about available completion and chat models.
    
    Returns:
        ModelInfo: Available models for completion and chat
    """
    # Access the state initialized in app.py's lifespan
    return request.app.state.model_info