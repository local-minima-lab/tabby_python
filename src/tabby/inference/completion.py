from pydantic import BaseModel, Field
from typing import List, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import yaml
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

def load_config(config_path: str = "LLM_config.yaml") -> CompletionOptions:
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f) or {}

    # 1. Pull the structural config from 'model' -> 'completion'
    completion_cfg = raw_config.get("model", {}).get("completion", {})
    engine_type = completion_cfg.get("engine")
    
    # Get settings for the specific engine (vllm or openai)
    engine_settings = completion_cfg.get(engine_type, {})
    
    # 2. Pull the global generation settings from 'inference'
    inference_data = raw_config.get("inference", {})

    # 3. Merge them into a single flat dictionary for Pydantic
    combined_data = {
        "engine_type": engine_type,
        **engine_settings,
        **inference_data
    }

    # 4. Security check: If API key is a placeholder, check environment variables
    if combined_data.get("api_key") == "PLACEHOLDER_DO_NOT_COMMIT":
        combined_data["api_key"] = os.getenv("OPENAI_API_KEY")

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