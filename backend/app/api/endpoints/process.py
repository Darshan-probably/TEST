from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks, Depends
from typing import Optional
import uuid
from pathlib import Path
from datetime import datetime

from app.api.models import ProcessRequest, ProcessResponse, OutputFormat
from app.core.config import settings
from app.core.exceptions import InvalidFileFormatError, ProcessingError
from app.processing.invoice_processor import InvoiceProcessor
from app.processing.pdf_converter import XlsxToPdfConverter
from app.utils.file import save_upload_file, clean_up_file, cleanup_old_files

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
    name: Optional[str] = Form(None),
    output_format: Optional[str] = Form("xlsx")
) -> ProcessRequest:
    """Validate and convert form data to request model"""
    return ProcessRequest(
        bags=int(bags) if bags and bags.strip() else None,
        weight=float(weight) if weight and weight.strip() else None,
        min_percent=float(min_percent) if min_percent else -2.0,
        max_percent=float(max_percent) if max_percent else 2.0,
        preserve_wrapping=preserve_wrapping.lower() == "true" if preserve_wrapping else True,
        template_type=template_type,
        date=date,
        address=address,
        lot_number=lot_number,
        name=name,
        output_format=output_format
    )

@router.post("/process/", response_model=ProcessResponse)
async def process_invoice(
    file: UploadFile = File(...),
    request: ProcessRequest = Depends(validate_request),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """API endpoint to process invoice file and provide download"""
    # Validate file extension
    if not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
        raise InvalidFileFormatError()
    
    # Generate unique ID
    unique_id = str(uuid.uuid4())
    
    # Define file paths
    input_filename = settings.UPLOAD_DIR / f"{unique_id}_{file.filename}"
    output_xlsx = settings.OUTPUT_DIR / f"{unique_id}_{file.filename.replace('.xlsx', '_processed.xlsx')}"
    output_pdf = settings.OUTPUT_DIR / f"{unique_id}_{file.filename.replace('.xlsx', '_processed.pdf')}"
    
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
        processed_xlsx_path = processor.process_file(str(input_filename), str(output_xlsx))
        
        # If PDF output requested, convert to PDF
        if request.output_format == OutputFormat.PDF:
            # Create PDF converter with configuration
            converter_config = {
                'include_header': True,
                'include_footer': True,
                'preserve_formatting': True,
                'footer_text': f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
            converter = XlsxToPdfConverter(converter_config)
            
            # Convert processed Excel file to PDF
            output_path = converter.convert(processed_xlsx_path, str(output_pdf))
            file_name = output_path.name
            media_type = "application/pdf"
        else:
            # Use Excel output
            output_path = Path(processed_xlsx_path)
            file_name = output_path.name
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        # Schedule cleanup tasks
        background_tasks.add_task(clean_up_file, input_filename)
        background_tasks.add_task(cleanup_old_files, settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.FILE_EXPIRY_HOURS)
        
        # Return download URL and file path
        download_url = f"/download/{file_name}"
        
        return ProcessResponse(
            download_url=download_url,
            file_path=str(output_path),
            format=request.output_format
        )
    
    except Exception as e:
        # Clean up files on error
        clean_up_file(input_filename)
        clean_up_file(output_xlsx)
        clean_up_file(output_pdf)
        raise ProcessingError(detail=str(e))