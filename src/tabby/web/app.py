import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.background import BackgroundTask

# Route imports
from .routes import health, server_setting, events, models
# Service imports
from tabby.services.event import start_event_service, stop_event_service

VERSION = "0.30.0-mgmt"
AUTOCOMPLETER_URL = "https://tabby-proxy-openai-26482401732.us-central1.run.app"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Start Logging Service
    await start_event_service()
    
    # 2. Setup a global HTTP client for forwarding
    # Using a single client is much faster than creating one per request
    app.state.client = httpx.AsyncClient(base_url=AUTOCOMPLETER_URL, timeout=60.0)
    
    print(f"🚀 Tabby Management 'Brain' {VERSION} Started")
    yield
    
    # 3. Shutdown
    await app.state.client.aclose()
    await stop_event_service()
    print("Stopping Management Service...")

app = FastAPI(title="Tabby Management Server", version=VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LOCAL ROUTES (Management & Metadata) ---
# These are handled by THIS container
app.include_router(health.router)
app.include_router(server_setting.router)
app.include_router(events.router)
app.include_router(models.router)

# --- PROXY ROUTE (The "Worker" Forwarder) ---
# This catches everything starting with /v1/ (like /v1/completions)
@app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_autocompleter(request: Request, path: str):
    """
    Acts as the entry point for completions. 
    Forward to the 'Slim' Autocompleter container.
    """
    # FUTURE: Firebase Auth logic goes here
    # if not is_authenticated(request): raise HTTPException(401)

    url = httpx.URL(path=f"/v1/{path}", query=request.url.query.encode("utf-8"))
    
    # Preserve original headers but let Cloud Run handle 'host'
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length"]}
    
    # Build the request to the worker
    rp_req = app.state.client.build_request(
        request.method, 
        url, 
        headers=headers, 
        content=request.stream()
    )
    
    # Send to Autocompleter
    rp_resp = await app.state.client.send(rp_req, stream=True)
    
    return Response(
        content=await rp_resp.aread(),
        status_code=rp_resp.status_code,
        headers=dict(rp_resp.headers),
        background=BackgroundTask(rp_resp.aclose)
    )

@app.get("/")
async def root():
    return {"status": "Management Node Active", "version": VERSION, "proxy_target": AUTOCOMPLETER_URL}