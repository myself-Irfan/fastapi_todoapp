from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List

from app.logger import get_logger
from app.taskapp.entities import DocumentCollection
from app.taskapp.document_model import DocumentRead, DocumentCreate, DocumentUpdate

logger = get_logger(__name__)


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def _get_document_instance(self, user_id: int, collection_id: int) -> DocumentCollection | None:
        return (
            self.db.query(DocumentCollection)
            .filter_by(id=collection_id, user_id=user_id)
            .first()
        )

    def fetch_documents(self, user_id: int) -> List[DocumentRead]:
        try:
            documents = self.db.query(DocumentCollection).filter_by(
                user_id=user_id
            ).all()

            return [DocumentRead.model_validate(document) for document in documents]
        except SQLAlchemyError as sql_err:
            logger.error("task retrival failed", error_type="database error", error=sql_err, exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error("task retrival failed", error_type="unexpected error", error=e, exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e

    def fetch_documents_by_id(self, user_id: int, document_id: int) -> DocumentRead | None:
        try:
            document = self._get_document_instance(user_id, document_id)

            if not document:
                logger.warning("task not found", document_id=document_id)
                return None

            return DocumentRead.model_validate(document)
        except SQLAlchemyError as sql_err:
            logger.error("document retrival failed", type="database error", document_id=document_id, error=sql_err, exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error("document retrival failed", type="unexpected error", document_id=document_id, error=e, exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e

    def create_document(self, user_id: int, doc_col_data: DocumentCreate) -> int:
        try:
            new_doc_col = DocumentCollection(**doc_col_data.model_dump(), user_id=user_id)
            self.db.add(new_doc_col)
            self.db.commit()
            self.db.refresh(new_doc_col)

            return new_doc_col.id
        except SQLAlchemyError as sql_err:
            self.db.rollback()
            logger.error("document collection creation failed", type="database error", error=sql_err, exc_info=True)
            raise SQLAlchemyError(f"Database error while creating task: {sql_err}") from sql_err
        except Exception as e:
            self.db.rollback()
            logger.error("document collection creation failed", type="unexpected error", error=e, exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e

    def update_document(self, user_id: int, document_id: int, doc_col_data: DocumentUpdate) -> int | None:
        try:
            document = self._get_document_instance(user_id, document_id)

            if not document:
                logger.warning("document not found for update", document_id=document_id)
                return None

            for key, value in doc_col_data.model_dump(exclude_unset=True).items():
                setattr(document, key, value)

            self.db.commit()
            self.db.refresh(document)

            return document.id
        except SQLAlchemyError as sql_err:
            logger.error("document update failed", type=sql_err, error=sql_err, document_id=document_id, exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error("document update failed", type="unexpected error", error=e, document_id=document_id, exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e

    def delete_collection(self, user_id: int, collection_id: int) -> bool:
        try:
            collection = self._get_document_instance(user_id, collection_id)

            if not collection:
                logger.warning("collection deletion failed", error="collection not found", document_id=collection_id)
                return False

            self.db.delete(collection)
            self.db.commit()
            return True
        except SQLAlchemyError as sql_err:
            logger.error("collection deletion failed", type="database error", document_id=collection_id, error=sql_err, exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error("collection deletion failed", type="unexpected error", document_id=collection_id, error=e, exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e