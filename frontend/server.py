"""
Frontend server for invoice processing application
"""
import os
from pathlib import Path
from typing import Optional
import logging

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Invoice Processor Frontend")

# Add CORS middleware to allow frontend to communicate with backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates" 

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Get the API URL from environment variable or use default
API_URL = os.environ.get("API_URL", "http://localhost:8000")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML page with API URL injected as JS variable"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "api_url": API_URL,
            "title": "Invoice Processor"
        }
    )

@app.get("/file_preview/{filename}", response_class=HTMLResponse)
async def file_preview(
    request: Request,
    filename: str,
    metadata: str = ""
):
    """Serve the file preview page"""
    return templates.TemplateResponse(
        "file_preview.html", 
        {
            "request": request,
            "api_url": API_URL,
            "filename": filename,
            "metadata": metadata,
            "title": "File Preview"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "frontend"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)