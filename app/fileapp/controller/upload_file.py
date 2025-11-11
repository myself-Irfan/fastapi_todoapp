from fastapi import status, UploadFile, File, Form, APIRouter, HTTPException
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from app.auth.dependencies import CurrentUser
from app.fileapp.exceptions import FileUploadException
from app.fileapp.model import FileReadResponse
from app.fileapp.dependencies import DependsFileUploadService
from app.logger import get_logger

router = APIRouter()

logger = get_logger(__name__)

@router.post(
    "/upload",
    response_model=FileReadResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    summary="upload a file",
    description="upload a file. optionally link with a document.",
    responses={
        201: {
            "description": "file uploaded successfully",
            "model": FileReadResponse
        },
        400: {"description": "invalid file or parameters"},
        404: {"description": "document not found"},
        500: {"description": "internal server error"}
    }
)
def upload_file(
    current_user: CurrentUser,
    file_upload_service: DependsFileUploadService,
    file: UploadFile = File(...),
    document_id: Optional[int] = Form(None, description="document id to link file with"),
) -> FileReadResponse:
    logger.info(
        "file upload request received",
        filename=file.filename,
        user_id=current_user.id,
        document_id=document_id
    )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no filename provided"
        )

    try:
        file_upload_service.upload_file(
            file=file,
            user_id=current_user.id,
            document_id=document_id
        )
        return FileReadResponse(message="file upload successful")

    except FileUploadException as e:
        logger.error("file upload error", error=str(e), status_code=e.status_code)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except SQLAlchemyError as sql_err:
        logger.error("database error", error=sql_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error occurred"
        )
    except Exception as err:
        logger.error("unexpected error", error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unexpected error occurred"
        )