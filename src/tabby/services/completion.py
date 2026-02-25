import uuid
from typing import Optional, AsyncGenerator
from tabby.common.api.completion import CompletionRequest, CompletionResponse, Choice

class CompletionService:
    def __init__(self, config, engine, prompt_builder, next_edit_builder):
        self.config = config
        self.engine = engine
        self.prompt_builder = prompt_builder
        self.next_edit_builder = next_edit_builder

    def _get_prompt(self, request: CompletionRequest) -> str:
        """Helper to centralize prompt building logic."""
        language = request.language or "unknown"
        if request.mode == "next_edit_suggestion":
            return self.next_edit_builder.build_prompt(request.segments.edit_history)
        
        snippets = self.prompt_builder.extract_snippets(request.segments)
        return self.prompt_builder.build(language, request.segments, snippets)

    async def generate(self, request: CompletionRequest, user_agent: Optional[str] = None) -> CompletionResponse:
        completion_id = f"cmpl-{uuid.uuid4()}"
        prompt = self._get_prompt(request)

        full_text = ""
        # Accumulate all chunks for a single final response
        async for chunk in self.engine.generate(prompt, request):
            full_text += chunk
        
        return CompletionResponse(
            id=completion_id,
            choices=[Choice(index=0, text=full_text)],
            mode=request.mode
        )

    async def generate_stream(self, request: CompletionRequest, user_agent: Optional[str] = None) -> AsyncGenerator[CompletionResponse, None]:
        """New method for streaming ghost text to the IDE."""
        completion_id = f"cmpl-{uuid.uuid4()}"
        prompt = self._get_prompt(request)

        # Yield each chunk as it comes out of vLLM
        async for chunk in self.engine.generate(prompt, request):
            yield CompletionResponse(
                id=completion_id,
                choices=[Choice(index=0, text=chunk)], # Only the new part
                mode=request.mode
            )