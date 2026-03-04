from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
from tabby.inference import CompletionOptions, CompletionStream
import asyncio
import uuid

class VLLMEngine(CompletionStream):
    def __init__(self, model_path: str):
        # Using AsyncEngineArgs to configure the engine for asynchronous operation
        engine_args = AsyncEngineArgs(
            model="Qwen/Qwen2.5-Coder-1.5B",
            gpu_memory_utilization=0.7,
            # Additional vLLM arguments can be added here
        )
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    async def generate(self, prompt: str, options: CompletionOptions):
        """
        Generates code completions asynchronously, matching the trait in completion.rs.
        """
        sampling_params = SamplingParams(
            temperature=float(getattr(options, "sampling_temperature", 0.1) or getattr(options, "temperature", 0.1) or 0.1),
            max_tokens=int(getattr(options, "max_decoding_tokens", 128) or 128),
            stop=getattr(options, "stop", None),
            seed=int(options.seed) if (hasattr(options, "seed") and options.seed is not None) else None,
            # vLLM's presence_penalty matches CompletionOptions
            presence_penalty=float(getattr(options, "presence_penalty", 0.0) or 0.0)
        )
        
        # Unique request ID for vLLM
        request_id = str(uuid.uuid4())
        
        # Streaming generation
        results_generator = self.engine.generate(prompt, sampling_params, request_id)
        
        last_output_text = ""
        async for request_output in results_generator:
            # vLLM returns the full cumulative text, so we yield only the new part
            full_text = request_output.outputs[0].text
            new_text = full_text[len(last_output_text):]
            last_output_text = full_text
            yield new_text