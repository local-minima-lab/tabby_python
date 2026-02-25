from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Route imports
from .routes import health, server_setting, events, models, completion # Added completion
from .routes.models import ModelInfo 

# Service imports
from tabby.services.event import start_event_service, stop_event_service, create_event_logger
from tabby.services.health import create_health_state
from tabby.services.completion import CompletionService
from tabby.services.completion_prompt import PromptBuilder
from tabby.services.next_edit_prompt import NextEditPromptBuilder
from tabby.inference.vllm_engine import VLLMEngine # Your inference implementation
from tabby.common.config import Config

VERSION = "0.30.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # 1. Print Banner
    print(rf"""
████████╗ █████╗ ██████╗ ██████╗ ██╗   ██╗
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
   ██║   ███████║██████╔╝██████╔╝ ╚████╔╝ 
   ██║   ██╔══██║██╔══██╗██╔══██╗  ╚██╔╝   
   ██║   ██║   ██║██████╔╝██████╔╝   ██║   
   ╚═╝   ╚═╝   ╚═╝╚═════╝ ╚═════╝    ╚═╝   

📄 Version {VERSION}
🚀 Server starting...
""")

    # 2. Setup Config & Event Service
    config = Config.load()
    app.state.config = config
    await start_event_service()
    
    # 3. Initialize Completion Engine & Service
    # (Matches the logic from the Rust version's initialization)
    model_cfg = config.model.completion or config.model.embedding
    model_path = getattr(model_cfg, "model_id", "Qwen/Qwen2.5-Coder-1.5B")

    engine = VLLMEngine(model_path=model_path)
    prompt_builder = PromptBuilder(code_search_params={}, prompt_template=None)
    next_edit_builder = NextEditPromptBuilder()
    
    # 4. Store Services in app.state for the Routes to use
    app.state.completion_service = CompletionService(
        config=config,
        engine=engine,
        prompt_builder=prompt_builder,
        next_edit_builder=next_edit_builder
    )
    
    app.state.health_state = create_health_state(model_config=config.model)
    app.state.model_info = ModelInfo.from_config(config)
    app.state.event_logger = create_event_logger()
    
    yield
    
    # 5. Shutdown
    await stop_event_service()

app = FastAPI(
    title="Tabby Server",
    description="Self-hosted AI coding assistant",
    version=VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Registering Routers ---
app.include_router(health.router)
app.include_router(server_setting.router)
app.include_router(events.router)
app.include_router(models.router)

# This adds /v1/completions to your server
app.include_router(completion.router, prefix="/v1")

@app.get("/")
async def root():
    return {
        "message": "Tabby Server",
        "version": VERSION,
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # Note: Running on 8080 to match your current setup
    uvicorn.run(app, host="0.0.0.0", port=8080)