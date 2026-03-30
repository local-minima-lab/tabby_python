# src/tabby/web/routes/models.py (Brain Version)
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/v1/models", tags=["models"])

class ModelCard(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "tabby"

@router.get("")
async def list_models():
    # Just return a placeholder so the IDE is happy
    return {
        "data": [
            ModelCard(id="tabby-openai-proxy")
        ]
    }