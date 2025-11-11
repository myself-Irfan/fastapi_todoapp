from fastapi.params import Depends
from typing import Annotated

from app.database.core import DbSession
from app.taskapp.document_service import DocumentService


def get_document_service(db: DbSession) -> DocumentService:
    return DocumentService(db=db)


DependsDocumentService = Annotated[DocumentService, Depends(get_document_service)]
