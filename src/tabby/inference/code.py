from typing import Optional, Any
from .decoding import StopCondition
from ..common.utils import clip_prompt # We'll define this in utils

class CodeGeneration:
    def __init__(self, engine: Any, additional_stop_words: list[str] = None):
        self.engine = engine
        self.stop_words = additional_stop_words or []

    async def generate(self, prompt: str, options: dict) -> str:
        # 1. Clip prompt (truncate from beginning)
        max_input_length = options.get("max_input_length", 1024)
        prompt = clip_prompt(prompt, max_input_length) if max_input_length > 0 else prompt

        # 2. Prepare completion options
        from .completion import CompletionOptions
        comp_options = CompletionOptions(
            max_decoding_tokens=options.get("max_decoding_tokens", 256),
            sampling_temperature=options.get("sampling_temperature", 0.1),
            seed=options.get("seed", 0)
        )

        # 3. Handle 'next_edit_suggestion' (Sync mode)
        if options.get("mode") == "next_edit_suggestion":
            return await self.engine.generate_sync(prompt, comp_options)

        # 4. Standard Mode (Streaming with stop conditions)
        generated_text = ""
        # The Rust code passes the language's specific stop words here
        stop_condition = StopCondition(self.stop_words, prompt)

        async for new_text in self.engine.generate(prompt, comp_options):
            should_stop, stop_length = stop_condition.should_stop(new_text)
            generated_text += new_text
            
            if should_stop:
                # Truncate the stop word from the generated text
                new_len = max(0, len(generated_text) - stop_length)
                generated_text = generated_text[:new_len]
                break
        
        return generated_text