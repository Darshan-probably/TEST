from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
from pathlib import Path

from app.api.models import PreviewRequest, PreviewResponse
from app.core.config import settings
from app.core.exceptions import InvalidFileFormatError, ProcessingError
from app.processing.invoice_processor import InvoiceProcessor
from app.utils.excel import convert_xlsx_to_preview_data
from app.utils.file import save_upload_file, clean_up_file

router = APIRouter()

def validate_request(
    bags: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
    min_percent: Optional[str] = Form("-2"),
    max_percent: Optional[str] = Form("2"),
    preserve_wrapping: Optional[str] = Form("true"),
    template_type: Optional[str] = Form("default"),
    date: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    lot_number: Optional[str] = Form(None),
    name: Optional[str] = Form(None)
) -> PreviewRequest:
    """Validate and convert form data to request model"""
    return PreviewRequest(
        bags=int(bags) if bags and bags.strip() else None,
        weight=float(weight) if weight and weight.strip() else None,
        min_percent=float(min_percent) if min_percent else -2.0,
        max_percent=float(max_percent) if max_percent else 2.0,
        preserve_wrapping=preserve_wrapping.lower() == "true" if preserve_wrapping else True,
        template_type=template_type,
        date=date,
        address=address,
        lot_number=lot_number,
        name=name
    )

@router.post("/preview/", response_model=PreviewResponse)
async def preview_invoice(
    file: UploadFile = File(...),
    request: PreviewRequest = Depends(validate_request),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """API endpoint to preview processed invoice file"""
    # Validate file extension
    if not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
        raise InvalidFileFormatError()
    
    # Generate unique ID
    unique_id = str(uuid.uuid4())
    
    # Define file paths
    input_filename = settings.UPLOAD_DIR / f"{unique_id}_preview_{file.filename}"
    output_filename = settings.OUTPUT_DIR / f"{unique_id}_preview_{file.filename}"
    
    try:
        # Save uploaded file
        await save_upload_file(file, input_filename)
        
        # Configure processor
        config = {
            'bag_count': request.bags,
            'target_weight': request.weight,
            'min_percent': request.min_percent,
            'max_percent': request.max_percent,
            'font_size': 9,  # Fixed font size to 9
            'preserve_wrapping': request.preserve_wrapping,
            'template_type': request.template_type,
            'date': request.date,
            'address': request.address,
            'lot_number': request.lot_number,
            'name': request.name
        }
        
        # Process file
        processor = InvoiceProcessor(config)
        output_path = processor.process_file(str(input_filename), str(output_filename))
        
        # Convert to preview data
        preview_data = convert_xlsx_to_preview_data(output_path, settings.MAX_PREVIEW_ROWS)
        
        # Include processing configuration in the response
        preview_data["config"] = {
            "bags": request.bags,
            "weight": request.weight,
            "minPercent": request.min_percent,
            "maxPercent": request.max_percent,
            "preserveWrapping": request.preserve_wrapping,
            "templateType": request.template_type,
            "date": request.date,
            "address": request.address,
            "lotNumber": request.lot_number,
            "name": request.name
        }
        
        # Include original and processed file IDs for later downloading
        preview_data["fileInfo"] = {
            "originalFile": input_filename.name,
            "processedFile": output_filename.name
        }
        
        # Schedule cleanup of temporary files
        background_tasks.add_task(clean_up_file, input_filename)
        background_tasks.add_task(clean_up_file, output_filename, settings.FILE_EXPIRY_HOURS)
        
        return preview_data
    
    except Exception as e:
        # Clean up files on error
        clean_up_file(input_filename)
        clean_up_file(output_filename)
        raise ProcessingError(detail=str(e))

