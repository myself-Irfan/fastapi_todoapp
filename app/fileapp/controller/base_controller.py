from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from app.auth.dependencies import CurrentUser, get_current_user
from app.fileapp.model import FileReadResponse, FileListResponse, ApiResponse
from app.logger import get_logger
from app.fileapp.services.base_service import FileService
from app.fileapp.controller.upload_file import router as upload_router
from app.fileapp.controller.download_file import router as download_router
from app.fileapp.dependencies import get_file_service

router = APIRouter(
    prefix="/api/files",
    tags=["Collection File APIs"],
    dependencies=[Depends(get_current_user)]
)
router.include_router(upload_router)
router.include_router(download_router)

logger = get_logger(__name__)


@router.get(
    "/",
    response_model=FileListResponse,
    summary="get all files",
    description="retrieve all files for current user. optionally filter by document id",
    responses={
        200: {
            "description": "files retrieval successful",
            "model": FileListResponse
        },
        500: {"description": "internal server error"}
    }
)
def get_all_files(
        current_user: CurrentUser,
        document_id: Optional[int] = Query(None, description="filter by document id"),
        file_service: FileService = Depends(get_file_service)
) -> FileListResponse:

    try:
        files = file_service.fetch_files(
            user_id=current_user.id,
            document_id=document_id
        )
        message = "files retrival success" if files else "no files to retrieve"

        return FileListResponse(
            message=message,
            data=files or []
        )
    except SQLAlchemyError as sql_err:
        logger.error("files retrival failed", error_type="database error", error=sql_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="files retrival failed"
        )
    except Exception as err:
        logger.error("files retrival failed", error_type="unexpected error", error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="files retrival failed"
        )


@router.get(
    "/{file_id}",
    response_model=FileReadResponse,
    summary="retrieve file by id",
    description="retrieve a file by its ID",
    responses={
        200: {
            "description": "file retrival success",
            "model": FileReadResponse
        },
        404: {"description": "file not found"},
        500: {"description": "internal server error"}
    }
)
def get_file(
        file_id: int,
        current_user: CurrentUser,
        file_service: FileService = Depends(get_file_service)
) -> FileReadResponse:

    try:
        file = file_service.fetch_file_by_id(
            user_id=current_user.id,
            file_id=file_id
        )

        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"file-{file_id} not found"
            )

        return FileReadResponse(
            message="file retrival successful",
            data=file
        )
    except HTTPException:
        raise
    except SQLAlchemyError as sql_err:
        logger.error("file retrival failed", error_type="database error", file_id=file_id, error=sql_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="file retrival failed"
        ) from sql_err
    except Exception as err:
        logger.error("file retrival failed", error_type="unexpected error", file_id=file_id, error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="file retrival failed"
        ) from err


@router.delete(
    "/{file_id}",
    response_model=ApiResponse,
    summary="delete a file",
    description="soft delete a file",
    responses={

    }
)
def delete_file(
        file_id: int,
        current_user: CurrentUser,
        file_service: FileService = Depends(get_file_service)
) -> ApiResponse:

    try:
        deleted = file_service.delete_file(
            user_id=current_user.id,
            file_id=file_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"file-{file_id} not found"
            )

        return ApiResponse(
            message=f"file-{file_id} deleted successfully"
        )
    except HTTPException:
        raise
    except SQLAlchemyError as sql_err:
        logger.error("file deletion failed", error_type="database error", file_id=file_id, error=sql_err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"file-{file_id} deletion failed"
        )
    except Exception as err:
        logger.error("file deletion failed", error_type="unexpected error", file_id=file_id, error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"file-{file_id} deletion failed"
        )