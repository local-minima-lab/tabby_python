from pydantic import BaseModel, Field
from typing import List, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import json
import os
from tabby.common.api import CompletionRequest

class CompletionOptions(BaseModel):
    # Identity & Engine Selection
    model_id: str
    engine_type: str
    
    # Engine-Specific (Optional based on which engine is active)
    api_key: Optional[str] = None
    dtype: Optional[str] = None
    gpu_memory_utilization: Optional[float] = None
    
    # Generation Settings
    max_decoding_tokens: int
    sampling_temperature: float
    seed: int
    presence_penalty: float
    
    # Tabby uses 'stop' tokens to prevent rambling or extra function generation
    stop: Optional[List[str]] = Field(default_factory=list)

def load_config(config_path: str) -> CompletionOptions:
    """
    Loads a flat YAML config from the provided path and 
    maps it to CompletionOptions.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    with open(config_path, 'r') as f:
        nested_data = json.load(f)
    
    # 1. Start with an empty dict
    combined_data = {}
    
    # 2. Extract and merge the fields from each section
    if "model" in nested_data:
        combined_data.update(nested_data["model"])
    
    if "inference" in nested_data:
        combined_data.update(nested_data["inference"])
        
    # 3. Now pass the flat dictionary to Pydantic
    return CompletionOptions(**combined_data)
class CompletionStream(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str,
        request: CompletionRequest, 
        options: CompletionOptions,
        stop: Optional[list[str]] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a completion in streaming mode (yields strings)"""
        pass

    async def generate_sync(
        self, 
        prompt: str,
        request: CompletionRequest, 
        options: CompletionOptions,
        stop: Optional[list[str]] = None
    ) -> str:
        """Non-streaming mode: collects all chunks into one string"""
        result = ""
        async for chunk in self.generate(prompt, request, options, stop):
            result += chunk
        return result