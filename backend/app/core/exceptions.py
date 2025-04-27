from fastapi import HTTPException, status

class InvalidFileFormatError(HTTPException):
    """Error raised when file format is not supported"""
    def __init__(self, detail="Only .xlsx files are supported"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class FileNotFoundError(HTTPException):
    """Error raised when requested file is not found"""
    def __init__(self, detail="File not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ProcessingError(HTTPException):
    """Error raised when processing fails"""
    def __init__(self, detail="Processing failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

