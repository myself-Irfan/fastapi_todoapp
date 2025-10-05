from fastapi import status, APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.auth.dependencies import CurrentUser
from app.taskapp.dependencies import DependsFileService
from app.logger import get_logger

router = APIRouter()

logger = get_logger(__name__)

@router.get(
    "/{file_id}/download",
    summary="download a file",
    description="download the actual file content",
    responses={
        200: {"description": "file downloaded successfully"},
        404: {"description": "file not found"},
        500: {"description": "internal server error"}
    }
)
async def download_file(file_id: int, current_user: CurrentUser, file_service: DependsFileService) -> FileResponse:

    try:
        file_metadata = file_service.fetch_file_by_id(
            user_id=current_user.id,
            file_id=file_id
        )

        if not file_metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"file-{file_id} not found"
            )

        file_path = file_service.get_file_path(
            user_id=current_user.id,
            file_id=file_id
        )

        if not file_path:
            logger.error("physical file not found", file_id=file_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="physical file not found in server"
            )

        return FileResponse(
            path=file_path,
            filename=file_metadata.title,
            media_type=file_metadata.mime_type
        )
    except HTTPException:
        raise
    except Exception as err:
        logger.error("file download failed", error_type="unknown error", file_id=file_id, error=err, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to download file"
        )