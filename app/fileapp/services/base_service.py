from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from fastapi import status

from app.logger import get_logger
from app.fileapp.entities import DocumentCollectionFile
from app.fileapp.model import FileRead
from app.fileapp.exceptions import FileNotFoundException, FileOperationException

logger = get_logger(__name__)


class FileService:
    def __init__(self, db: Session):
        self.db = db

    def _get_file_instance(self, user_id: int, file_id: int) -> DocumentCollectionFile:
        try:
            file = self.db.query(DocumentCollectionFile).filter_by(
                id=file_id,
                user_id=user_id,
                is_active=True
            ).first()
        except (SQLAlchemyError, OperationalError) as db_err:
            logger.error("file retrival failed", file_id=file_id, error=db_err, exc_info=True)
            raise FileOperationException(
                message=f'database error while retrieving file-{file_id}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) from db_err
        else:
            if not file:
                logger.warning("file not found", file_id=file_id)
                raise FileNotFoundException(f"file-{file_id} not found")
            return file

    def fetch_files(self, user_id: int, document_id: Optional[int] = None) -> List[FileRead]:
        try:
            query = self.db.query(DocumentCollectionFile).filter_by(
                user_id=user_id,
                is_active=True
            )

            if document_id is not None:
                query = query.filter_by(document_id=document_id)

            files = query.all()
            return [FileRead.model_validate(f) for f in files]
        except SQLAlchemyError as sql_err:
            logger.error("file retrival failed", error_type="database error", error=sql_err, exc_info=True)
            raise

    def fetch_file_by_id(self, user_id: int, file_id: int) -> FileRead:
        try:
            file = self._get_file_instance(user_id, file_id)

            return FileRead.model_validate(file)
        except FileNotFoundException:
            raise
        except SQLAlchemyError as sql_err:
            logger.error("file retrival failed", error_type="database error", file_id=file_id, error=sql_err, exc_info=True)
            raise sql_err

    def delete_file(self, user_id: int, file_id: int) -> bool:
        """
        soft delete a file.
        if no reference then delete from server
        """

        try:
            file = self._get_file_instance(user_id, file_id)

            if not file:
                logger.warning("file not found for deletion", file_id=file_id)
                raise FileNotFoundException(f"file-{file_id} not found")

            file.is_active = False
            self.db.commit()

            logger.info("file soft deletion successful", file_id=file_id)

            other_active_refs = (
                self.db.query(DocumentCollectionFile)
                .filter(
                    and_(
                        DocumentCollectionFile.checksum == file.checksum,
                        DocumentCollectionFile.is_active.is_(True),
                        DocumentCollectionFile.id != file_id
                    )
                )
                .count()
            )

            if other_active_refs == 0:
                try:
                    if os.path.exists(file.file_path):
                        os.remove(file.file_path)
                        logger.info("physical file deleted", path=file.file_path)
                except OSError as os_err:
                    logger.error("physical file deletion failed", path=file.file_path, error=os_err, error_type="os error", exc_info=True)
            else:
                logger.info("physical file preserved", active_refs=other_active_refs)

            return True
        except FileNotFoundException:
            raise
        except SQLAlchemyError as sql_err:
            self.db.rollback()
            logger.error("file deletion failed", error_type="database error", file_id=file_id, error=sql_err, exc_info=True)
            raise sql_err