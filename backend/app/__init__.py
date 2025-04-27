# app/__init__.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.core.config import settings
from app.api.routes import router as api_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(title=settings.APP_TITLE)
    
    # Ensure directories exist
    for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR]:
        Path(directory).mkdir(exist_ok=True, parents=True)
    
    # Mount static files
    if Path(settings.STATIC_DIR).exists():
        app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    # Root route
    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        """Serve the frontend"""
        index_path = Path(settings.STATIC_DIR) / "index.html"
        if index_path.exists():
            with open(index_path, "r") as f:
                return f.read()
        return "<html><body><h1>Excel Processor API</h1></body></html>"
    
    return app