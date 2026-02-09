"""
Tabby FastAPI application.

Main web server for Tabby code completion.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys

# Import routes
from .routes import health

# Create FastAPI app
app = FastAPI(
    title="Tabby Server",
    description="Self-hosted AI coding assistant",
    version="0.30.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware (permissive like Rust version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Print startup banner."""
    version = "0.30.0"
    print(r"""
████████╗ █████╗ ██████╗ ██████╗ ██╗   ██╗
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
   ██║   ███████║██████╔╝██████╔╝ ╚████╔╝ 
   ██║   ██╔══██║██╔══██╗██╔══██╗  ╚██╔╝  
   ██║   ██║  ██║██████╔╝██████╔╝   ██║   
   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚═════╝    ╚═╝   

📄 Version {version}
🚀 Server starting...
""")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Tabby Server",
        "version": "0.30.0",
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)