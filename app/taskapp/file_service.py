from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import UploadFile
import hashlib
import os
import shutil
from pathlib import Path

from app.logger import get_logger
from app.taskapp.entities import DocumentCollectionFile, DocumentCollection
from app.taskapp.file_model import FileRead, FileUpdate

logger = get_logger(__name__)


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    def _get_file_instance(self, user_id: int, file_id: int) -> DocumentCollectionFile | None:
        return (
            self.db.query(DocumentCollectionFile).filter_by(
                id=file_id,
                user_id=user_id,
                is_active=True
            ).first()
        )

    def _calculate_checksum(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda : f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def upload_file(self, file: UploadFile, user_id: int, document_id: Optional[int] = None) -> int:
        temp_path = None

        if document_id is not None:
            document_exists = self.db.query(
                DocumentCollection
            ).filter_by(
                id=document_id
            ).first()
            if not document_exists:
                raise ValueError(f"document-{document_id} does not exist")

        try:
            temp_filename = f"temp_{os.urandom(8).hex()}_{file.filename}"
            temp_path = self.upload_dir / temp_filename

            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            checksum = self._calculate_checksum(str(temp_path))
            file_size = os.path.getsize(temp_path)

            extension = Path(file.filename).suffix.lower() or ""
            mime_type = file.content_type or "application/octet-stream"
            file_title = file.filename

            existing_file = (
                self.db.query(DocumentCollectionFile)
                .filter_by(checksum=checksum)
                .first()
            )

            if existing_file:
                logger.info(
                    "file-deduplicated",
                    checksum=checksum[:8],
                    existing_file_id=existing_file.id
                )
                os.remove(temp_path)
                final_path=existing_file.file_path
            else:
                final_filename = f"{checksum}{extension}"
                final_path = str(self.upload_dir/final_filename)
                shutil.move(str(temp_path), final_path)
                logger.info("new file saved", path=final_path)

            new_file = DocumentCollectionFile(
                title=file_title,
                file_path=final_path,
                file_size=file_size,
                mime_type=mime_type,
                extension=extension,
                checksum=checksum,
                user_id=user_id,
                document_id=document_id
            )
            self.db.add(new_file)
            self.db.commit()
            self.db.refresh(new_file)

            logger.info("file record creation successful", file_id=new_file.id)
            return new_file.id

        except SQLAlchemyError as sql_err:
            self.db.rollback()
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error("file upload failed", error_type="database error", error=sql_err, exc_info=True)
            raise sql_err
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error("file upload failed", error_type="unexpected error", error=e, exc_info=True)
            raise SQLAlchemyError(f"unexpected error during file upload: {str(e)}") from e

    def fetch_files(self, user_id: int, document_id: Optional[int] = None) -> List[FileRead]:
        try:
            query = self.db.query(DocumentCollectionFile).filter_by(
                user_id=user_id,
                is_active=True
            )

            if document_id is not None:
                query = query.filter_by(
                    document_id=document_id
                )

            files = query.all()
            return [FileRead.model_validate(f) for f in files]
        except SQLAlchemyError as sql_err:
            logger.error("file retrival failed", error_type="database error", error=sql_err, exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error("file retrival failed", error_type="unexpected error", error=e, exc_info=True)
            raise SQLAlchemyError(f"unexpected error: {str(e)}") from e

    def fetch_file_by_id(self, user_id: int, file_id: int) -> FileRead | None:
        try:
            file = self._get_file_instance(user_id, file_id)

            if not file:
                logger.warning("file not found", file_id=file_id)
                return None

            return FileRead.model_validate(file)
        except SQLAlchemyError as sql_err:
            logger.error("file retrival failed", error_type="database error", file_id=file_id, error=sql_err, exc_info=True)
            raise sql_err
        except Exception as err:
            logger.error("file retrival failed", error_type="unknown error", file_id=file_id, error=err, exc_info=True)
            raise SQLAlchemyError(f"Unexpected error: {str(err)}")

    def delete_file(self, user_id: int, file_id: int) -> bool:
        """
        soft delete a file.
        if no reference then delete from server
        """

        try:
            file = self._get_file_instance(user_id, file_id)

            if not file:
                logger.warning("file not found for deletion", file_id=file_id)
                return None

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
        except SQLAlchemyError as sql_err:
            self.db.rollback()
            logger.error("file deletion failed", error_type="database error", file_id=file_id, error=sql_err, exc_info=True)
            raise sql_err
        except Exception as err:
            self.db.rollback()
            logger.error("file deletion failed", error_type="unknown error", file_id=file_id, error=err, exc_info=True)
            raise SQLAlchemyError(f"Unexpected error: {str(err)}")

    def get_file_path(self, user_id: int, file_id: int) -> str | None:
        try:
            file = self._get_file_instance(user_id, file_id)

            if not file:
                return None

            if not os.path.exists(file.file_path):
                logger.error("Physical file missing", file_id=file_id, path=file.file_path)
                return None

            return file.file_path
        except Exception as e:
            logger.error("file path retrival failed", file_id=file_id, error=e, exc_info=True)
            return None