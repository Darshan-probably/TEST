# app/core/config.py
"""
Configuration management for the Excel Processor application
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = BASE_DIR / "config.yaml"

# Template configuration defaults
DEFAULT_TEMPLATE = {
    'weight_column': 'G',
    'start_row': 8,
    'total_row': 38,
    'bag_count_cell': 'C38',
    'font_size': 9,
    'min_percent': -2,
    'max_percent': 2,
    'preserve_wrapping': True,
    'date_cell': 'A4',
    'lot_number_cell': 'B4',
    'name_cell': 'C3',
    'address_cell': 'C4',
}

class Settings:
    """
    Application settings loaded from config file with defaults
    """
    def __init__(self):
        self.config_data = self._load_config()
        
        # Set up directories with defaults
        self.upload_dir = Path(self.get_setting("paths.upload_dir", "uploads"))
        self.output_dir = Path(self.get_setting("paths.output_dir", "outputs"))
        self.react_build_dir = Path(self.get_setting("paths.react_build_dir", "../frontend/build"))
        
        # Create directories if they don't exist
        for directory in [self.upload_dir, self.output_dir]:
            directory.mkdir(exist_ok=True, parents=True)
            
        # Set up application settings
        self.file_expiry_hours = self.get_setting("app.file_expiry_hours", 1)
        self.max_preview_rows = self.get_setting("app.max_preview_rows", 20)
        self.allowed_extensions = self.get_setting("app.allowed_extensions", [".xlsx"])
        self.allowed_output_formats = self.get_setting("app.allowed_output_formats", ["xlsx", "pdf"])
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file if it exists"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                return yaml.safe_load(f)
        return {}
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """
        Get a setting from config using dot notation path
        
        Args:
            path: Dot notation path to setting (e.g., "app.file_expiry_hours")
            default: Default value if setting not found
            
        Returns:
            Setting value or default if not found
        """
        parts = path.split(".")
        value = self.config_data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
                
        return value
    
    def get_template_config(self, template_type: str = 'default') -> Dict[str, Any]:
        """
        Get configuration for a specific template type
        
        Args:
            template_type: Template identifier
            
        Returns:
            Template configuration dictionary
        """
        templates = self.get_setting("templates", {})
        template = templates.get(template_type, DEFAULT_TEMPLATE)
        
        # Start with default and update with template-specific values
        result = DEFAULT_TEMPLATE.copy()
        result.update(template)
        return result
    
    def get_pdf_settings(self, profile: str = 'default') -> Dict[str, Any]:
        """
        Get PDF conversion settings for a specific profile
        
        Args:
            profile: PDF settings profile identifier
            
        Returns:
            PDF settings dictionary
        """
        pdf_settings = self.get_setting("pdf_settings", {})
        return pdf_settings.get(profile, pdf_settings.get('default', {}))

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached)
    
    Returns:
        Settings object
    """
    return Settings()