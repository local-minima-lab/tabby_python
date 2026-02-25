"""
Server settings API types.

Defines server configuration that can be exposed via API.
"""

from pydantic import BaseModel, Field


class ServerSetting(BaseModel):
    """Server settings exposed to clients."""
    
    # Add these two fields
    model: str = Field(default="tabby-python-backend", description="The completion model name")
    chat_model: str = Field(default="tabby-python-backend", description="The chat model name")
    
    disable_client_side_telemetry: bool = Field(
        default=False,
        description="Whether client-side telemetry is disabled"
    )