from fastapi.params import Depends
from typing import Annotated

from app.database.core import DbSession
from app.fileapp.services.base_service import FileService
from app.fileapp.services.download_service import FileDownloadService
from app.fileapp.services.upload_service import FileUploadService


def get_file_service(db: DbSession) -> FileService:
    return FileService(db=db)

def get_file_upload_service(db: DbSession) -> FileUploadService:
    return FileUploadService(db=db)

def get_file_download_service(db: DbSession) -> FileDownloadService:
    return FileDownloadService(db=db)


DependsFileService = Annotated[FileService, Depends(get_file_service)]
DependsFileUploadService = Annotated[FileUploadService, Depends(get_file_upload_service)]
DependsFileDownloadService = Annotated[FileDownloadService, Depends(get_file_download_service)]