# app/core/constants.py
"""
Constants used throughout the application
"""
from enum import Enum
from reportlab.lib.pagesizes import letter, A4

class TemplateType(str, Enum):
    """Template type enumeration"""
    DEFAULT = "default"
    INVOICE1 = "invoice1"
    INVOICE2 = "invoice2"
    CUSTOM = "custom"

class OutputFormat(str, Enum):
    """Output format enumeration"""
    XLSX = "xlsx"
    PDF = "pdf"

class PdfProfile(str, Enum):
    """PDF profile enumeration"""
    DEFAULT = "default"
    COMPACT = "compact"
    LETTER = "letter"

# PDF page sizes
PDF_PAGE_SIZES = {
    "a4": A4,
    "letter": letter,
}

# API endpoints
API_ENDPOINTS = {
    'process': '/api/process/',
    'preview': '/api/preview/',
    'convert': '/api/convert-to-pdf/',
    'download': '/api/download/',
}

# MIME types
MIME_TYPES = {
    'xlsx': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    'pdf': "application/pdf",
}