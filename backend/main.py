from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List, Union
import shutil
import os
import uuid
import tempfile
import base64
from pathlib import Path
from invoice_processor import InvoiceProcessor
import openpyxl
import io
# In main.py, add:
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files from the React build

# Create app
app = FastAPI(title="Invoice Processor")

UPLOAD_DIR = Path("backend/uploads")
OUTPUT_DIR = Path("backend/outputs")
STATIC_DIR = Path("backend/static")
REACT_BUILD_DIR = Path("frontend/build")  # Path to React build directory

# Ensure directories exist
for directory in [UPLOAD_DIR, OUTPUT_DIR, STATIC_DIR]:
    directory.mkdir(exist_ok=True)

# Mount React static files
if REACT_BUILD_DIR.exists():
    app.mount("/static", StaticFiles(directory=REACT_BUILD_DIR), name="static")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse(os.path.join(REACT_BUILD_DIR, "index.html"))


# Create index.html if it doesn't exist
INDEX_PATH = STATIC_DIR / "index.html"
if not INDEX_PATH.exists():
    with open(INDEX_PATH, "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Invoice Processor</title>
    <meta http-equiv="refresh" content="0;url=/">
</head>
<body>
    <p>Redirecting...</p>
</body>
</html>""")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Clean up old files periodically
def cleanup_old_files():
    """Remove files older than 1 hour"""
    import time
    current_time = time.time()
    one_hour = 60 * 60
    
    for directory in [UPLOAD_DIR, OUTPUT_DIR]:
        for file_path in directory.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > one_hour:
                    file_path.unlink()

@app.get("/", response_class=HTMLResponse)
async def get_upload_page():
    """Return the main HTML page"""
    with open(INDEX_PATH, "r") as file:
        return file.read()

def convert_xlsx_to_preview_data(xlsx_path, max_rows=20):
    """
    Convert the first few rows of an Excel file to a JSON-friendly structure
    for preview rendering
    """
    try:
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        
        # Get column headers (using row 1)
        headers = []
        for col in range(1, ws.max_column + 1):
            cell_value = ws.cell(row=1, column=col).value
            headers.append(str(cell_value) if cell_value is not None else "")
        
        # Get data rows (limited to max_rows)
        rows = []
        for row in range(2, min(ws.max_row + 1, max_rows + 2)):
            row_data = []
            for col in range(1, ws.max_column + 1):
                cell_value = ws.cell(row=row, column=col).value
                row_data.append(str(cell_value) if cell_value is not None else "")
            rows.append(row_data)
            
        # Include additional metadata
        metadata = {
            "totalRows": ws.max_row,
            "totalColumns": ws.max_column,
            "sheetName": ws.title,
            "previewRows": len(rows)
        }
            
        return {
            "headers": headers,
            "rows": rows,
            "metadata": metadata
        }
    except Exception as e:
        print(f"Error creating preview: {str(e)}")
        return {"error": str(e)}

@app.post("/preview/")
async def preview_invoice_upload(
    file: UploadFile = File(...),
    bags: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
    font_size: Optional[str] = Form(None),
    font_name: Optional[str] = Form(None),
    min_percent: Optional[str] = Form("-2"),
    max_percent: Optional[str] = Form("2"),
    preserve_wrapping: Optional[str] = Form("true")
):
    """API endpoint to preview processed invoice file"""
    # Convert form values to appropriate types
    bags_int = int(bags) if bags and bags.strip() else None
    weight_float = float(weight) if weight and weight.strip() else None
    font_size_int = int(font_size) if font_size and font_size.strip() else None
    min_percent_float = float(min_percent) if min_percent else -2
    max_percent_float = float(max_percent) if max_percent else 2
    preserve_wrapping_bool = preserve_wrapping.lower() == "true" if preserve_wrapping else True
    
    unique_id = str(uuid.uuid4())
    
    try:
        # Validate file extension
        if not file.filename.lower().endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
        
        # Save uploaded file temporarily
        input_filename = UPLOAD_DIR / f"{unique_id}_preview_{file.filename}"
        output_filename = OUTPUT_DIR / f"{unique_id}_preview_{file.filename}"
        
        # Save uploaded file
        with open(input_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Configure processor
        config = {
            'min_percent': min_percent_float,
            'max_percent': max_percent_float,
            'font_size': font_size_int,
            'font_name': font_name,
            'preserve_wrapping': preserve_wrapping_bool
        }
        
        if bags_int is not None:
            config['bag_count'] = bags_int
        
        if weight_float is not None:
            config['target_weight'] = weight_float
        
        # Process file
        processor = InvoiceProcessor(config)
        output_path = processor.process_file(str(input_filename), str(output_filename))
        
        # Convert to preview data
        preview_data = convert_xlsx_to_preview_data(output_path)
        
        # Include processing configuration in the response
        preview_data["config"] = {
            "bags": bags_int,
            "weight": weight_float,
            "fontSize": font_size_int,
            "fontName": font_name,
            "minPercent": min_percent_float,
            "maxPercent": max_percent_float,
            "preserveWrapping": preserve_wrapping_bool
        }
        
        # Include original and processed file IDs for later downloading
        preview_data["fileInfo"] = {
            "originalFile": input_filename.name,
            "processedFile": output_filename.name
        }
        
        return preview_data
    except Exception as e:
        # Log the complete error
        import traceback
        print(f"Error processing preview: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Preview error: {str(e)}")

@app.post("/process/")
async def process_invoice_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    bags: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
    font_size: Optional[str] = Form(None),
    font_name: Optional[str] = Form(None),
    min_percent: Optional[str] = Form("-2"),
    max_percent: Optional[str] = Form("2"),
    preserve_wrapping: Optional[str] = Form("true")
):
    """API endpoint to process uploaded invoice file"""
    # Clean up old files
    background_tasks.add_task(cleanup_old_files)
    
    # Convert form values to appropriate types
    bags_int = int(bags) if bags and bags.strip() else None
    weight_float = float(weight) if weight and weight.strip() else None
    font_size_int = int(font_size) if font_size and font_size.strip() else None
    min_percent_float = float(min_percent) if min_percent else -2
    max_percent_float = float(max_percent) if max_percent else 2
    preserve_wrapping_bool = preserve_wrapping.lower() == "true" if preserve_wrapping else True
    
    unique_id = str(uuid.uuid4())
    
    try:
        # Validate file extension
        if not file.filename.lower().endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
        
        # Save uploaded file
        input_filename = UPLOAD_DIR / f"{unique_id}_{file.filename}"
        output_filename = OUTPUT_DIR / f"{unique_id}_processed_{file.filename}"
        
        # Save uploaded file
        with open(input_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Configure processor
        config = {
            'min_percent': min_percent_float,
            'max_percent': max_percent_float,
            'font_size': font_size_int,
            'font_name': font_name,
            'preserve_wrapping': preserve_wrapping_bool
        }
        
        if bags_int is not None:
            config['bag_count'] = bags_int
        
        if weight_float is not None:
            config['target_weight'] = weight_float
        
        # Process file
        processor = InvoiceProcessor(config)
        output_path = processor.process_file(str(input_filename), str(output_filename))
        
        return {
            "message": "Invoice processed successfully",
            "download_url": f"/download/{output_filename.name}"
        }
    except Exception as e:
        # Log the complete error
        import traceback
        print(f"Error processing file: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a processed file"""
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path, 
        filename=filename.split('_', 2)[-1],  # Remove UUID prefix
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# For Replit compatibility
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app",port=port, reload=True)