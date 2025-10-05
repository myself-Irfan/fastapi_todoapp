from fastapi.params import Depends
from typing import Annotated

from app.database.core import DbSession
from app.taskapp.document_service import DocumentService
from app.taskapp.file_service import FileService


def get_document_service(db: DbSession) -> DocumentService:
    return DocumentService(db=db)

def get_file_service(db: DbSession) -> FileService:
    return FileService(db=db)

DependsDocumentService = Annotated[DocumentService, Depends(get_document_service)]
DependsFileService = Annotated[FileService, Depends(get_file_service)]