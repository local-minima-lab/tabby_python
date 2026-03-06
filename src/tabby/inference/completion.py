from pydantic import BaseModel, Field
from typing import List
from abc import ABC, abstractmethod
from typing import AsyncGenerator
import yaml
from typing import Optional
from tabby.common.api import CompletionRequest

class CompletionOptions(BaseModel):
    model_id: str
    max_decoding_tokens: int
    sampling_temperature: float
    seed: int
    presence_penalty: float
    # Tabby uses 'stop' tokens to prevent the model from 
    # hallucinating extra functions or rambling.
    stop: Optional[List[str]] = Field(default_factory=list)

def load_config(config_path: str = "LLM_config.yaml") -> CompletionOptions:
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f) or {}

    # 1. Pull the model_id from the 'model' -> 'completion' section
    model_cfg = raw_config.get("model", {}).get("completion", {})
    model_id = model_cfg.get("model_id")

    # 2. Pull the rest of the settings from the 'inference' section
    inference_data = raw_config.get("inference", {})

    # 3. Merge them together before passing to Pydantic
    combined_data = {
        "model_id": model_id,
        **inference_data
    }

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
        # Equivalent to 'while let Some(chunk) = stream.next().await'
        async for chunk in self.generate(prompt, request, options, stop):
            result += chunk
        return result
