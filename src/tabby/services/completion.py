import uuid
from typing import Optional, AsyncGenerator
from tabby.common.api.completion import CompletionRequest, CompletionResponse, Choice
from tabby.common.languages import get_language

class CompletionService:
    def __init__(self, config, options, engine, prompt_builder, next_edit_builder):
        self.config = config
        self.options = options
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
    
    def _get_stop_words(self, request: CompletionRequest) -> list[str]:
        stops = []
        
        # 1. Automatically grab the "EOS" token from your current model
        # This replaces the need for the YAML list!
        if hasattr(self.engine, 'tokenizer'):
            eos_token = self.engine.tokenizer.eos_token
            if eos_token:
                stops.append(eos_token)

        # 2. Get language-specific keywords from your languages.py
        lang = request.language
        lang_config = get_language(lang) if lang else None
        
        if lang_config:
            stops.extend(lang_config.get_stop_words())
        
        return list(set(stops))

    async def generate(self, request: CompletionRequest, user_agent: Optional[str] = None) -> CompletionResponse:
        completion_id = f"cmpl-{uuid.uuid4()}"
        prompt = self._get_prompt(request)
        stop_words = self._get_stop_words(request)

        full_text = ""
        # Accumulate all chunks for a single final response
        async for chunk in self.engine.generate(prompt, request, self.options, stop=stop_words):
            full_text += chunk
        
        return CompletionResponse(
            id=completion_id,
            choices=[Choice(index=0, text=full_text)],
            mode=request.mode
        )

    async def generate_stream(self, request: CompletionRequest, user_agent: Optional[str] = None) -> AsyncGenerator[CompletionResponse, None]:
        completion_id = f"cmpl-{uuid.uuid4()}"
        prompt = self._get_prompt(request)
        # Don't forget to inject them here too!
        stop_words = self._get_stop_words(request)

        # Pass the stop_words to the engine
        async for chunk in self.engine.generate(prompt, request, self.options, stop=stop_words):
            yield CompletionResponse(
                id=completion_id,
                choices=[Choice(index=0, text=chunk)],
                mode=request.mode
        )