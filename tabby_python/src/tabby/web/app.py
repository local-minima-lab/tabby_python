from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import os
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
from tabby.inference.openai_engine import OpenAIEngine
from tabby.common.config import Config
from tabby.inference.completion import load_config
from tabby.inference import vllm_engine, openai_engine
import yaml
from dotenv import load_dotenv

VERSION = "0.30.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(dotenv_path=env_path)
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

    # 2. Setup Paths
    # Adjust this to point to your root project directory
    BASE_DIR = Path(__file__).resolve().parents[3] 
    main_config_path = BASE_DIR / "main.yaml"

    # 3. Load the Main Config (The "Pointer")
    print(f"🔍 Reading main config from: {main_config_path}")
    if not main_config_path.exists():
        raise FileNotFoundError(f"Main config not found at {main_config_path}")

    with open(main_config_path, 'r') as f:
        main_cfg = yaml.safe_load(f)

    # Determine which engine to use
    active_key = main_cfg.get("active_engine", "local_vllm")
    specific_config_rel_path = main_cfg["engines"][active_key]["config_path"]
    specific_config_path = BASE_DIR / specific_config_rel_path

    # 4. Load Engine-Specific Inference Options
    print(f"📦 Loading {active_key} settings from: {specific_config_path}")
    options = load_config(str(specific_config_path))
    app.state.inference_options = options

    # 5. Consolidated Engine Factory
    # Instead of nested functions, we use a simple if/else block
    forced_engine = os.environ.get("FORCE_ENGINE")

    if forced_engine:
        print(f"⚠️ Overriding YAML: Forced engine set to {forced_engine}")
        engine_to_use = forced_engine
    else:
        engine_to_use = options.engine_type
    if engine_to_use == "openai":
        print("🚀 Booting up OpenAI Engine...")
        api_key = os.environ.get("OPENAI_API_KEY")
        engine = OpenAIEngine(api_key=api_key, model_name=options.model_id)
    else:
        print(f"🏠 Booting up Local vLLM Engine ({options.model_id}) on RTX 4060...")
        # vLLM takes the whole options object for hardware settings
        engine = VLLMEngine(options)

    # 6. Initialize Services
    await start_event_service()
    event_logger = create_event_logger()
    app.state.event_logger = event_logger
    # We pass the shared 'engine' and 'options' here
    app.state.completion_service = CompletionService(
        config=Config.load(),
        options=options,
        engine=engine,
        prompt_builder=PromptBuilder(code_search_params={}, prompt_template=None),
        next_edit_builder=NextEditPromptBuilder(),
        event_logger=event_logger
    )

    # 7. Setup Remaining State
    tabby_config = Config.load()
    app.state.config = tabby_config
    app.state.health_state = create_health_state(model_config=Config.load().model)
    app.state.model_info = ModelInfo.from_config(Config.load())

    yield

    # 8. Shutdown
    print("Server shutting down...")
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