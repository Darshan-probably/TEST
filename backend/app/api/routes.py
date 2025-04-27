from fastapi import APIRouter, Depends
from app.api.endpoints import process, preview, convert, download

router = APIRouter()

# Include all endpoint routers
router.include_router(process.router, tags=["process"])
router.include_router(preview.router, tags=["preview"])
router.include_router(convert.router, tags=["convert"])
router.include_router(download.router, tags=["download"])

# Root endpoint to serve the React frontend
@router.get("/", include_in_schema=False)
async def read_root():
    """Serve the React frontend"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path
    from app.core.config import settings
    
    index_path = Path(settings.REACT_BUILD_DIR) / "index.html"
    if index_path.exists():
        with open(index_path, "r") as f:
            return HTMLResponse(content=f.read())
    else:
        return {"message": "Excel Processor API"}