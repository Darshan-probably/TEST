from fastapi import APIRouter, Path
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.exceptions import FileNotFoundError

router = APIRouter()

@router.get("/download/{file_name}")
async def download_file(file_name: str = Path(...)):
    """Download processed file"""
    file_path = settings.OUTPUT_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError()
    
    # Determine MIME type based on file extension
    if file_name.lower().endswith('.pdf'):
        media_type = "application/pdf"
    else:
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Extract original filename by removing UUID prefix
    original_name = file_name.split('_', 1)[1] if '_' in file_name else file_name
    
    return FileResponse(
        path=file_path,
        filename=original_name,
        media_type=media_type
    )
