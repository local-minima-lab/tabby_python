from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from tabby.inference.completion import CompletionStream, CompletionOptions
from tabby.common.api import CompletionRequest

class OpenAIEngine(CompletionStream):
    def __init__(self, api_key: str, model_name: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name

    async def generate(
        self, 
        prompt: str,
        request: CompletionRequest, 
        options: CompletionOptions,
        stop: Optional[list[str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream completions from OpenAI's Chat Completion API.
        """
        # Use the provided stop tokens or fallback to config defaults
        stop_tokens = options.stop if options.stop else None

        response = await self.client.completions.create(
            model=self.model_name,
            prompt=prompt,
            temperature=options.sampling_temperature,
            max_tokens=options.max_decoding_tokens,
            presence_penalty=options.presence_penalty,
            seed=options.seed,
            stop=stop_tokens,
            stream=True
        )

        async for chunk in response:
            # OpenAI's streaming response delivers content in the 'delta' field
            if chunk.choices and chunk.choices[0].text:
                yield chunk.choices[0].text