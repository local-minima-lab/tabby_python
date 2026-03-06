from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
from tabby.inference import CompletionOptions, CompletionStream
import asyncio
import uuid
from tabby.common.api import CompletionRequest
from typing import Optional

class VLLMEngine(CompletionStream):
    def __init__(self, model_path: str):
        # Using AsyncEngineArgs to configure the engine for asynchronous operation
        engine_args = AsyncEngineArgs(
            model= model_path,
            gpu_memory_utilization=0.7,
            # Additional vLLM arguments can be added here
        )
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    async def generate(self, prompt: str, request: CompletionRequest, options: CompletionOptions, stop: Optional[list[str]] = None):
        """
        Generates code completions asynchronously, matching the trait in completion.rs.
        """
        sampling_params = SamplingParams(
            temperature=float(options.sampling_temperature),
            max_tokens=int(options.max_decoding_tokens),
            # CHANGE THIS: Use the 'stop' argument passed from the service
            stop=stop if stop is not None else getattr(options, "stop", None),
            seed=int(options.seed),
            presence_penalty=float(options.presence_penalty)
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