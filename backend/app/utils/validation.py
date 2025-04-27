# app/utils/validation.py
"""
Input validation utilities
"""
import re
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def validate_excel_file(filename: str, allowed_extensions: List[str] = [".xlsx"]) -> bool:
    """
    Validate Excel file extension
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if valid
    """
    if not filename:
        return False
        
    for ext in allowed_extensions:
        if filename.lower().endswith(ext.lower()):
            return True
    
    return False

def validate_date_format(date_str: str, formats: List[str] = ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]) -> Optional[datetime]:
    """
    Validate and parse date string
    
    Args:
        date_str: Date string to validate
        formats: List of date formats to try
        
    Returns:
        Datetime object if valid, None otherwise
    """
    if not date_str:
        return None
        
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def sanitize_number(value: Optional[Union[str, int, float]]) -> Optional[float]:
    """
    Sanitize and convert a numeric value
    
    Args:
        value: Value to sanitize
        
    Returns:
        Float value if valid, None otherwise
    """
    if value is None:
        return None
        
    if isinstance(value, (int, float)):
        return float(value)
        
    if isinstance(value, str):
        # Remove non-numeric characters except decimal point and negative sign
        value = re.sub(r'[^\d.-]', '', value)
        try:
            return float(value)
        except ValueError:
            return None
    
    return None

def validate_request_params(params: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, str]:
    """
    Validate request parameters
    
    Args:
        params: Parameters to validate
        required_fields: List of required field names
        
    Returns:
        Dictionary of validation errors (empty if valid)
    """
    errors = {}
    required_fields = required_fields or []
    
    # Check required fields
    for field in required_fields:
        if field not in params or params[field] is None:
            errors[field] = f"Field '{field}' is required"
    
    # Validate specific fields
    if 'min_percent' in params and params['min_percent'] is not None:
        try:
            min_pct = float(params['min_percent'])
            if min_pct < -100 or min_pct > 100:
                errors['min_percent'] = "Min percent must be between -100 and 100"
        except ValueError:
            errors['min_percent'] = "Min percent must be a number"
    
    if 'max_percent' in params and params['max_percent'] is not None:
        try:
            max_pct = float(params['max_percent'])
            if max_pct < -100 or max_pct > 100:
                errors['max_percent'] = "Max percent must be between -100 and 100"
        except ValueError:
            errors['max_percent'] = "Max percent must be a number"
    
    # Validate date field if present
    if 'date' in params and params['date']:
        if validate_date_format(params['date']) is None:
            errors['date'] = "Invalid date format. Use YYYY-MM-DD"
    
    return errors