import os
import httpx
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Tabby specific imports
from tabby.services.completion import CompletionService
from tabby.services.completion_prompt import PromptBuilder
from tabby.services.next_edit_prompt import NextEditPromptBuilder
from tabby.inference.openai_engine import OpenAIEngine
from tabby.common.config import Config
from tabby.inference.completion import load_config
from .routes import completion 

VERSION = "0.30.0-stable-hijack"
SERVICES_URL = "https://your-services-container.a.run.app/log"

class SimpleLogger:
    def log(self, *args, **kwargs): pass

# Send to other container for the rest of the services
async def send_to_logging_service(payload: dict):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(SERVICES_URL, json=payload, timeout=2.0)
        except Exception:
            pass 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Starting Stable Autocompleter (v{VERSION})")

    # Load config and env
    BASE_DIR = Path(__file__).resolve().parents[3] 
    openai_config_path = BASE_DIR / "configs" / "openai_engine.yaml"
    options = load_config(str(openai_config_path))
    
    dotenv_path = BASE_DIR / ".env"

    if dotenv_path.exists():
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    clean_key = key.strip()
                    clean_value = value.strip().strip("'").strip('"')
                    os.environ[clean_key] = clean_value
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing!")

    engine = OpenAIEngine(api_key=api_key, model_name=options.model_id)
    service = CompletionService(
        config=Config.load(),
        options=options,
        engine=engine,
        prompt_builder=PromptBuilder(code_search_params={}, prompt_template=None),
        next_edit_builder=NextEditPromptBuilder(),
        event_logger=SimpleLogger()
    )

    # 4. THE HIJACK (Silent Mode)
    original_generate = service.generate
    original_generate_stream = service.generate_stream

    async def tutor_generate(request, *args, **kwargs):
        # INJECTION POINT (Blank for now)
        # request.segments.prefix += "" 
        
        response = await original_generate(request, *args, **kwargs)
        
        if response.choices:
            text = response.choices[0].text
            #print(f"🤖 OUTPUT: '{text[:50].strip()}...'") 
        return response

    def tutor_generate_stream(request, *args, **kwargs):
        # INJECTION POINT (Blank for now)
        # request.segments.prefix += ""
        return original_generate_stream(request, *args, **kwargs)

    service.generate = tutor_generate
    service.generate_stream = tutor_generate_stream

    app.state.completion_service = service
    yield
    print("🛑 Shutting down...")

app = FastAPI(title="Tabby Tutor Proxy", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(completion.router, prefix="/v1")

@app.get("/")
async def root():
    return {"message": "Tutor Proxy is Active (Stable/No-Injection)"}

@app.get("/v1/health")
async def health():
    return {
        "model": "gpt-5.1-codex-mini", 
        "status": "ready",
        "tutor_mode": False,
        "version": VERSION
    }