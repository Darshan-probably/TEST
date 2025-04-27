# app/utils/file.py
"""
File handling utilities
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Union
import logging

from fastapi import UploadFile

logger = logging.getLogger(__name__)

async def save_upload_file(upload_file: UploadFile, destination: Union[str, Path]) -> Path:
    """
    Save uploaded file to destination
    
    Args:
        upload_file: FastAPI UploadFile object
        destination: Destination path
        
    Returns:
        Path to the saved file
    """
    destination = Path(destination)
    
    # Create directory if it doesn't exist
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file in chunks to handle large files
    with open(destination, "wb") as buffer:
        while content := await upload_file.read(1024 * 1024):  # 1MB chunks
            buffer.write(content)
    
    logger.debug(f"Saved uploaded file to {destination}")
    return destination

def clean_up_file(file_path: Union[str, Path], expiry_hours: Optional[int] = None) -> None:
    """
    Delete a file or schedule it for deletion after expiry period
    
    Args:
        file_path: Path to file
        expiry_hours: Hours after which file should be deleted (None for immediate deletion)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return
    
    if expiry_hours is None:
        # Delete immediately
        try:
            os.unlink(file_path)
            logger.debug(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
    else:
        # Set file metadata with expiry time
        # This just logs the scheduled deletion time for now
        # In a production system, you'd use a task queue or similar
        expiry_time = datetime.now() + timedelta(hours=expiry_hours)
        logger.debug(f"Scheduled file {file_path} for deletion at {expiry_time}")

def cleanup_old_files(upload_dir: Union[str, Path], output_dir: Union[str, Path], expiry_hours: int) -> int:
    """
    Clean up expired files in upload and output directories
    
    Args:
        upload_dir: Upload directory path
        output_dir: Output directory path
        expiry_hours: Expiry period in hours
        
    Returns:
        Number of files deleted
    """
    upload_dir, output_dir = Path(upload_dir), Path(output_dir)
    cutoff_time = datetime.now() - timedelta(hours=expiry_hours)
    deleted_count = 0
    
    # Process both directories
    for directory in [upload_dir, output_dir]:
        if not directory.exists():
            continue
            
        for file_path in directory.glob('*'):
            if not file_path.is_file():
                continue
                
            # Check file modification time
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mod_time < cutoff_time:
                try:
                    os.unlink(file_path)
                    deleted_count += 1
                    logger.debug(f"Deleted expired file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete expired file {file_path}: {e}")
    
    if deleted_count > 0:
        logger.info(f"Cleaned up {deleted_count} expired files")
    
    return deleted_count

def get_file_info(file_path: Union[str, Path]) -> dict:
    """
    Get information about a file
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {"exists": False}
    
    stats = file_path.stat()
    
    return {
        "exists": True,
        "name": file_path.name,
        "size": stats.st_size,
        "created": datetime.fromtimestamp(stats.st_ctime),
        "modified": datetime.fromtimestamp(stats.st_mtime),
        "extension": file_path.suffix.lower(),
    }