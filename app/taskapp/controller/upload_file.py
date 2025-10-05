from fastapi import status, UploadFile, File, Form, HTTPException, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from app.auth.dependencies import CurrentUser
from app.taskapp.file_model import FileReadResponse
from app.taskapp.dependencies import DependsFileService
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
        500: {"description": "internal server error"}
    }
)
async def upload_file(
        current_user: CurrentUser,
        file_service: DependsFileService,
        file: UploadFile = File(...),
        document_id: Optional[int] = Form(None, description="document id to link file with"),
) -> FileReadResponse:
    logger.info(
        "file upload request received",
        filename=file.filename,
        user_id=current_user.id,
        document_id=document_id
    )

    try:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="no filename provided"
            )

        file_id = await file_service.upload_file(
            file=file,
            user_id=current_user.id,
            document_id=document_id
        )

        return FileReadResponse(
            message=f"file-{file_id} upload successful"
        )

    except ValueError as val_err:
        logger.warning("invalid file upload", error=str(val_err))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err)
        )
    except SQLAlchemyError as sql_err:
        logger.error("file upload failed", error_type="database error", error=sql_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unexpected error occurred"
        ) from sql_err
    except Exception as err:
        logger.error("file upload failed", error_type="unexpected error", error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unexpected error occurred"
        ) from err