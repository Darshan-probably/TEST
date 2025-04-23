# config.py
"""
Configuration settings for the Excel Processor application
"""
from reportlab.lib.pagesizes import letter, A4

# Default template settings
DEFAULT_TEMPLATE = {
    'weight_column': 'G',           # Column containing weights
    'start_row': 8,                 # First row for weight data
    'total_row': 38,                # Row containing total
    'bag_count_cell': 'C38',        # Cell containing bag count text
    'font_size': 9,                 # Default font size for weights
    'min_percent': -2,              # Default minimum weight variation (%)
    'max_percent': 2,               # Default maximum weight variation (%)
    'preserve_wrapping': True,      # Preserve text wrapping when adding rows
    'date_cell': 'A4',              # Cell for date
    'lot_number_cell': 'B4',        # Cell for lot number
    'name_cell': 'C3',              # Cell for name
    'address_cell': 'C4',           # Cell for address
}

# Additional template configurations
INVOICE_TEMPLATE_1 = {
    'weight_column': 'F',
    'start_row': 10,
    'total_row': 40,
    'bag_count_cell': 'B40',
    'date_cell': 'A3',
    'lot_number_cell': 'B3',
    'name_cell': 'C2',
    'address_cell': 'C3',
}

INVOICE_TEMPLATE_2 = {
    'weight_column': 'H',
    'start_row': 12,
    'total_row': 42,
    'bag_count_cell': 'D42',
    'date_cell': 'A5',
    'lot_number_cell': 'B5',
    'name_cell': 'C4',
    'address_cell': 'C5',
}

CUSTOM_TEMPLATE = {
    # This is a flexible template that can be configured at runtime
    # All parameters will be provided by the user during processing
    'weight_column': 'G',
    'start_row': 10,
    'total_row': 40,
    'bag_count_cell': 'C40',
    'date_cell': 'A4',
    'lot_number_cell': 'B4',
    'name_cell': 'C3',
    'address_cell': 'C4',
}

# Template mapping
TEMPLATE_CONFIGS = {
    'default': DEFAULT_TEMPLATE,
    'invoice1': INVOICE_TEMPLATE_1,
    'invoice2': INVOICE_TEMPLATE_2,
    'custom': CUSTOM_TEMPLATE,
}

# PDF conversion settings
PDF_CONVERSION_SETTINGS = {
    'default': {
        'page_size': A4,
        'include_header': True,
        'include_footer': True,
        'preserve_formatting': True,
        'margin': 36,  # 0.5 inch in points
    },
    'compact': {
        'page_size': A4,
        'include_header': False,
        'include_footer': False,
        'preserve_formatting': True,
        'margin': 18,  # 0.25 inch in points
    },
    'letter': {
        'page_size': letter,
        'include_header': True,
        'include_footer': True,
        'preserve_formatting': True,
        'margin': 36,  # 0.5 inch in points
    },
}

# Application settings
APP_SETTINGS = {
    'upload_dir': 'uploads',
    'output_dir': 'outputs',
    'file_expiry_hours': 1,  # Files are deleted after this many hours
    'max_preview_rows': 20,  # Maximum number of rows to include in preview
    'allowed_extensions': ['.xlsx'],
    'allowed_output_formats': ['xlsx', 'pdf'],
}

# API endpoints
API_ENDPOINTS = {
    'process': '/process/',
    'preview': '/preview/',
    'convert': '/convert-to-pdf/',
    'download': '/download/',
}

def get_template_config(template_type='default'):
    """
    Get configuration for a specific template type
    
    Args:
        template_type (str): Template identifier
        
    Returns:
        dict: Template configuration dictionary
    """
    return TEMPLATE_CONFIGS.get(template_type, DEFAULT_TEMPLATE).copy()

def get_app_setting(setting_name):
    """
    Get an application setting
    
    Args:
        setting_name (str): Setting name
        
    Returns:
        any: Setting value or None if not found
    """
    return APP_SETTINGS.get(setting_name)

def get_pdf_settings(profile='default'):
    """
    Get PDF conversion settings for a specific profile
    
    Args:
        profile (str): PDF settings profile identifier
        
    Returns:
        dict: PDF settings dictionary
    """
    return PDF_CONVERSION_SETTINGS.get(profile, PDF_CONVERSION_SETTINGS['default']).copy()