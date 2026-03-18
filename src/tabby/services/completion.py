import uuid
from typing import Optional, AsyncGenerator
from tabby.common.api.completion import CompletionRequest, CompletionResponse, Choice
from tabby.common.languages import get_language
from tabby.common.api.event import CompletionEvent, Choice as EventChoice

class CompletionService:
    def __init__(self, config, options, engine, prompt_builder, next_edit_builder, event_logger):
        self.config = config
        self.options = options
        self.engine = engine
        self.prompt_builder = prompt_builder
        self.next_edit_builder = next_edit_builder
        self.event_logger = event_logger

    def _get_prompt(self, request: CompletionRequest) -> str:
        """Helper to centralize prompt building logic."""
        language = request.language or "unknown"
        if request.mode == "next_edit_suggestion":
            return self.next_edit_builder.build_prompt(request.segments.edit_history)
        
        snippets = self.prompt_builder.extract_snippets(request.segments)
        return self.prompt_builder.build(language, request.segments, snippets)
    
    def _get_stop_words(self, request: CompletionRequest) -> list[str]:
        # 1. Check if the YAML config already has a hardcoded stop list (Priority)
        # This will catch your OpenAI YAML settings.
        stops = list(getattr(self.options, 'stop', []) or [])

        lang = request.language
        lang_config = get_language(lang) if lang else None

        if lang_config:
            toml_stops = lang_config.get_stop_words()
            # Add TOML stops if they aren't already in the list
            for word in toml_stops:
                if word not in stops:
                    stops.append(word)
        
        # Grab model-specific EOS token (if local vLLM)
        if hasattr(self.engine, 'tokenizer'):
            eos_token = getattr(self.engine.tokenizer, 'eos_token', None)
            if eos_token and eos_token not in stops:
                stops.append(eos_token)

        return stops

    async def generate(self, request: CompletionRequest, user_agent: Optional[str] = None) -> CompletionResponse:
        completion_id = f"cmpl-{uuid.uuid4()}"
        full_text = ""
        # Accumulate all chunks for a single final response
        async for response in self.generate_stream(request, user_agent):
            full_text += response.choices[0].text

        event_segments = None
        if request.segments:
            event_segments = request.segments.model_dump()

        event = CompletionEvent(
            completion_id=completion_id,
            language=request.language or "unknown",
            prompt=self._get_prompt(request),
            segments=event_segments,
            choices=[EventChoice(index=0, text=full_text)],
            user_agent=user_agent
        )

        self.event_logger.log(user=None, event=event)
        
        return CompletionResponse(
            id=completion_id,
            choices=[Choice(index=0, text=full_text)],
            mode=request.mode
        )
    

    async def generate_stream(self, request: CompletionRequest, user_agent: Optional[str] = None):
        completion_id = f"cmpl-{uuid.uuid4()}"
        prompt = self._get_prompt(request)
        all_stops = self._get_stop_words(request)

        # NATIVE ROUTE (vLLM / Non-OpenAI)
        if self.options.engine_type != "openai":
            async for chunk in self.engine.generate(prompt, request, self.options, stop=all_stops):
                yield CompletionResponse(
                    id=completion_id,
                    choices=[Choice(index=0, text=chunk)],
                    mode=request.mode
                )
            return

        # INTERCEPTOR ROUTE (OpenAI)
        api_stops = all_stops[:4]      # Only the first 4 (Model Tags + \n\n)
        soft_stops = all_stops[4:]     # The overflow (Language Keywords)
        
        full_text_seen = ""

        async for chunk in self.engine.generate(prompt, request, self.options, stop=api_stops):
            full_text_seen += chunk
            
            # Check if any "Soft Stop" word (like 'public' or 'def') appeared
            should_stop = False
            for stop_word in soft_stops:
                if stop_word in full_text_seen:
                    # We found a stop word that OpenAI didn't know about!
                    should_stop = True
                    break
            
            if should_stop:
                # If we hit a soft stop, we cut the stream immediately
                break

            yield CompletionResponse(
                id=completion_id,
                choices=[Choice(index=0, text=chunk)],
                mode=request.mode
            )
        
