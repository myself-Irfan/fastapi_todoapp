from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import hashlib
import shutil
from typing import Optional, Set
import os
import magic
import mimetypes

from app.config import settings
from app.logger import get_logger
from app.taskapp.entities import DocumentCollection
from app.fileapp.entities import DocumentCollectionFile
from app.fileapp.exceptions import DocumentNotFoundException, InvalidFileTypeException, FileProcessingException, FileUploadException

logger = get_logger(__name__)


class FileUploadService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = settings.upload_dir
        self.upload_dir.mkdir(exist_ok=True)

        self.allowed_extensions: Set[str] = settings.allowed_extensions_set

        self.extension_to_mime = {}
        for ext in self.allowed_extensions:
            mime_type, _ = mimetypes.guess_type(f"file{ext}")
            if mime_type:
                self.extension_to_mime[ext] = mime_type

        self.allowed_mime_types = set(self.extension_to_mime.values())

    def __check_document_collection_exist(self, document_id: int) -> bool:
        return self.db.get(DocumentCollection, document_id) is not None

    def __save_temp_file(self, file: UploadFile) -> Path:
        temp_filename = f"temp_{os.urandom(8).hex()}_{file.filename}"
        temp_path = self.upload_dir / temp_filename

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return temp_path

    def __validate_file_type(self, temp_path: Path, file_name: str) -> bool:
        extension = Path(file_name).suffix.lower()
        real_mime_type = magic.from_file(str(temp_path), mime=True)

        if extension not in self.allowed_extensions:
            logger.warning(
                "File type not allowed",
                filename=file_name
            )
            return False

        expected_mime = self.extension_to_mime.get(extension)
        if real_mime_type != expected_mime:
            logger.warning(
                'File rejected. File type does not match extension',
                filename=file_name,
                expected_type=expected_mime,
                detected_type=real_mime_type
            )
            return False

        return True

    def __calculate_checksum(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda : f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def upload_file(self, file: UploadFile, user_id: int, document_id: Optional[int] = None):
        temp_path = None

        if document_id is not None:
            document_exists: bool = self.__check_document_collection_exist(document_id)
            if not document_exists:
                raise DocumentNotFoundException(f"document_collection-{document_id} does not exist")

        try:
            temp_path = self.__save_temp_file(file)

            if not self.__validate_file_type(temp_path, file.filename):
                raise InvalidFileTypeException("file type mismatch or not allowed")

            checksum = self.__calculate_checksum(str(temp_path))
            file_size = os.path.getsize(temp_path)
            extension = Path(file.filename).suffix.lower()
            mime_type = file.content_type
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
                temp_path = None
                final_path=existing_file.file_path
            else:
                final_filename = f"{checksum}{extension}"
                final_path = str(self.upload_dir/final_filename)
                shutil.move(str(temp_path), final_path)
                temp_path = None
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

        except SQLAlchemyError as sql_err:
            self.db.rollback()
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error("file upload failed", error_type="database error", error=sql_err, exc_info=True)
            raise
        except FileUploadException:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            raise
        except Exception as e:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error("file upload failed", error_type="unexpected error", error=e, exc_info=True)
            raise FileProcessingException(f"unexpected error during file upload: {str(e)}") from e


# TODO: save mime_type from magic?