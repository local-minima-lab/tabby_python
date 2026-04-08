from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from tabby.inference.completion import CompletionStream, CompletionOptions
from tabby.common.api.completion import CompletionRequest
from httpx import Timeout

class OpenAIEngine(CompletionStream):
    def __init__(self, api_key: str, model_name: str, config: dict):
        timeout_cfg = config.get("inference", {}).get("timeout", {})
        # The SDK handles the wss:// connection logic internally
        custom_timeout = Timeout(
            timeout=timeout_cfg.get("total"), 
            connect=timeout_cfg.get("connect")
        )
        self.client = AsyncOpenAI(api_key=api_key, timeout=custom_timeout)
        self.model_name = model_name

    async def generate(
        self, 
        prompt: str,
        request: CompletionRequest, 
        options: CompletionOptions,
        stop: Optional[list[str]] = None
    ) -> AsyncGenerator[str, None]:
    
        async with self.client.realtime.connect(model=self.model_name) as connection:
            
            # 1. Update Session
            await connection.session.update(session={
                "type": "realtime",
                "output_modalities": ["text"],
                "instructions": ("You are a code completion engine."
                                "Continue the user's code exactly where it leaves off."
                                "Do not provide explanations, markdown backticks, or preamble."
                                "Only output the missing code tokens."
                )
            })

            # 2. THE FIX: Use the nested conversation.item path
            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }
            )

            # 3. THE FIX: Use the nested response path
            await connection.response.create()

            # 4. Listen for Events
            async for event in connection:
                if event.type in ["response.text.delta", "response.output_text.delta"]:
                    yield event.delta
                
                elif event.type == "response.content_part.added":
                    if hasattr(event, 'part') and event.part.type == 'text':
                        # Some versions send the initial text here
                        yield event.part.text

                elif event.type == "response.done":
                    # Check if the response was 'filtered' or 'failed'
                    if event.response.status == "failed":
                        print(f"⚠️ Response Failed: {event.response.status_details}")
                    break
                    
                elif event.type == "error":
                    print(f"❌ Realtime Error: {event.error.message}")
                    break