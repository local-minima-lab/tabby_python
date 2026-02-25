import asyncio
from typing import AsyncGenerator

class LlamaEngine:
    def __init__(self, model_path: str):
        self.model_path = model_path
        print(f"🛠️ Mock LlamaEngine initialized with path: {model_path}")

    async def generate(self, prompt: str, options=None) -> AsyncGenerator[str, None]:
        """
        Mock generation: Yields 'Hello World' one piece at a time.
        """
        # We simulate a tiny bit of 'thinking' time
        await asyncio.sleep(0.1)
        
        # Yielding strings mimics how a real LLM streams tokens
        yield "\n# Hello from Python Tabby!"
        
        await asyncio.sleep(0.2)
        yield "\nprint('Hello World')"
        
        # In a real engine, we would continue yielding tokens here