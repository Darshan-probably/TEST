from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks, Depends
from typing import Optional
import uuid
from pathlib import Path
from datetime import datetime

from app.api.models import ConvertToPdfRequest, ConvertResponse
from app.core.config import settings
from app.core.exceptions import InvalidFileFormatError, ProcessingError
from app.processing.pdf_converter import XlsxToPdfConverter
from app.utils.file import save_upload_file, clean_up_file, cleanup_old_files

router = APIRouter()

def validate_request(
    include_header: Optional[str] = Form("true"),
    include_footer: Optional[str] = Form("true"),
    preserve_formatting: Optional[str] = Form("true"),
    page_size: Optional[str] = Form("A4")
) -> ConvertToPdfRequest:
    """Validate and convert form data to request model"""
    return ConvertToPdfRequest(
        include_header=include_header.lower() == "true" if include_header else True,
        include_footer=include_footer.lower() == "true" if include_footer else True,
        preserve_formatting=preserve_formatting.lower() == "true" if preserve_formatting else True,
        page_size=page_size
    )

@router.post("/convert-to-pdf/", response_model=ConvertResponse)
async def convert_to_pdf(
    file: UploadFile = File(...),
    request: ConvertToPdfRequest = Depends(validate_request),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """API endpoint to convert Excel file to PDF"""
    # Validate file extension
    if not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
        raise InvalidFileFormatError()
    
    # Generate unique ID
    unique_id = str(uuid.uuid4())
    
    # Define file paths
    input_filename = settings.UPLOAD_DIR / f"{unique_id}_{file.filename}"
    output_filename = settings.OUTPUT_DIR / f"{unique_id}_{file.filename.replace('.xlsx', '.pdf')}"
    
    try:
        # Save uploaded file
        await save_upload_file(file, input_filename)
        
        # Determine page size
        from reportlab.lib.pagesizes import letter, A4
        page_size_value = letter if request.page_size.lower() == "letter" else A4
        
        # Configure converter
        config = {
            'include_header': request.include_header,
            'include_footer': request.include_footer,
            'preserve_formatting': request.preserve_formatting,
            'page_size': page_size_value,
            'footer_text': f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }
        
        # Convert Excel to PDF
        converter = XlsxToPdfConverter(config)
        output_path = converter.convert(str(input_filename), str(output_filename))
        
        # Schedule cleanup tasks
        background_tasks.add_task(clean_up_file, input_filename)
        background_tasks.add_task(cleanup_old_files, settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.FILE_EXPIRY_HOURS)
        
        # Return download URL and file path
        file_name = output_filename.name
        download_url = f"/download/{file_name}"
        
        return ConvertResponse(
            download_url=download_url,
            file_path=str(output_path)
        )
    
    except Exception as e:
        # Clean up files on error
        clean_up_file(input_filename)
        clean_up_file(output_filename)
        raise ProcessingError(detail=str(e))
