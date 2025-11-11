from fastapi import status


class FileOperationException(Exception):
    """
    base exception for file operations (read, download, delete)
    """
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message: str = message
        self.status_code: int = status_code
        super().__init__(self.message)

class FileNotFoundException(FileOperationException):
    """
    file not found
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class FileDeletionException(FileOperationException):
    """
    file deletion fails
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class FileUploadException(Exception):
    """
    base exception class for file upload operations
    """
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message: str = message
        self.status_code: int = status_code
        super().__init__(self.message)

class DocumentNotFoundException(FileUploadException):
    """
    document collection does not exist
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class InvalidFileTypeException(FileUploadException):
    """
    file type validation fails
    """
    def __init__(self, message: str):
        super().__init__(message)

class FileProcessingException(FileUploadException):
    """
    file processing failed
    """
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)