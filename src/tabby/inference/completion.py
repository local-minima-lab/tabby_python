from pydantic import BaseModel, Field
from typing import List
from abc import ABC, abstractmethod
from typing import AsyncGenerator

class CompletionOptions(BaseModel):
    max_decoding_tokens: int = 64
    sampling_temperature: float = 0.1
    seed: int = 0
    # Tabby uses 'stop' tokens to prevent the model from 
    # hallucinating extra functions or rambling.
    stop: List[str] = Field(default_factory=list)

class CompletionStream(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        options: CompletionOptions
    ) -> AsyncGenerator[str, None]:
        """Generate a completion in streaming mode (yields strings)"""
        pass

    async def generate_sync(
        self, 
        prompt: str, 
        options: CompletionOptions
    ) -> str:
        """Non-streaming mode: collects all chunks into one string"""
        result = ""
        # Equivalent to 'while let Some(chunk) = stream.next().await'
        async for chunk in self.generate(prompt, options):
            result += chunk
        return result
