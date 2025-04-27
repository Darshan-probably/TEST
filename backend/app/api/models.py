from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class TemplateType(str, Enum):
    """Supported template types"""
    DEFAULT = "default"
    INVOICE1 = "invoice1"
    INVOICE2 = "invoice2"
    CUSTOM = "custom"

class OutputFormat(str, Enum):
    """Supported output formats"""
    XLSX = "xlsx"
    PDF = "pdf"

class PDFProfile(str, Enum):
    """Supported PDF profiles"""
    DEFAULT = "default"
    COMPACT = "compact" 
    LETTER = "letter"

class PreviewRequest(BaseModel):
    """Preview request model"""
    bags: Optional[int] = None
    weight: Optional[float] = None
    min_percent: float = -2.0
    max_percent: float = 2.0
    preserve_wrapping: bool = True
    template_type: TemplateType = TemplateType.DEFAULT
    date: Optional[str] = None
    address: Optional[str] = None
    lot_number: Optional[str] = None
    name: Optional[str] = None

class ProcessRequest(PreviewRequest):
    """Process request model extending preview request"""
    output_format: OutputFormat = OutputFormat.XLSX

class ConvertToPdfRequest(BaseModel):
    """PDF conversion request model"""
    include_header: bool = True
    include_footer: bool = True
    preserve_formatting: bool = True
    page_size: str = "A4"
    
    @validator("page_size")
    def validate_page_size(cls, v):
        if v.upper() not in ["A4", "LETTER"]:
            raise ValueError("page_size must be either 'A4' or 'letter'")
        return v

class PreviewResponse(BaseModel):
    """Preview response model"""
    headers: List[str]
    rows: List[List[str]]
    metadata: Dict[str, Any]
    config: Dict[str, Any]
    fileInfo: Dict[str, str]

class ProcessResponse(BaseModel):
    """Process response model"""
    download_url: str
    file_path: str
    format: str

class ConvertResponse(BaseModel):
    """Convert response model"""
    download_url: str
    file_path: str