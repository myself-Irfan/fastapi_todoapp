from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.auth.dependencies import CurrentUser, get_current_user
from app.taskapp.dependencies import DependsDocumentService
from app.taskapp.document_model import DocumentCreate, DocumentListResponse, DocumentResponse, DocumentUpdate, ApiResponse
from app.logger import get_logger

router = APIRouter(
    prefix="/api/tasks",
    tags=["Task APIs"],
    dependencies=[Depends(get_current_user)]
)
logger = get_logger(__name__)


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="Get all documents",
    description="Retrieve all documents from the database",
    responses={
        200: {
            "description": "Documents retrieved successfully",
            "model": DocumentListResponse
        },
        500: {"description": "Internal server error"}
    }
)
def get_all_tasks(current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentListResponse:
    try:
        tasks = document_service.fetch_documents(user_id=current_user.id)

        message = "Collections retrieved successfully" if tasks else f"No collection found for {current_user.name}"

        return DocumentListResponse(
            message=message,
            data=tasks or []
        )
    except SQLAlchemyError as e:
        logger.error("document retrival failed", error_type="database error", error=e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching tasks"
        ) from e
    except Exception as e:
        logger.error("document retrival failed", error_type="unexpected error", error=e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) from e


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary='Get a document by ID',
    description='Retrieve a specific document by its ID',
    responses={
        200: {
            'description': 'Document retrieved successfully',
            'model': DocumentResponse
        },
        404: {'description': 'Document not found'},
        500: {'description': 'Internal server error'}
    }
)
def get_task(document_id: int, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentResponse:
    try:
        task = document_service.fetch_documents_by_id(document_id=document_id, user_id=current_user.id)

        if not task:
            logger.warning('task not found', document_id=document_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with ID {document_id} not found'
            )

        return DocumentResponse(
            message='Collection retrieved successfully',
            data=task
        )
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        logger.error('task retrival failed', error=err, error_type="database error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while fetching task-{document_id}'
        ) from err
    except Exception as err:
        logger.error('task retrival failed', error=err, error_type="unexpected error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An unexpected error occurred'
        ) from err


@router.post(
    "/",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new Document object',
    description='Add a Document object to DocumentCollection table database',
    responses={
        201: {
            'description': 'Document created',
            'model': ApiResponse
        },
        500: {'description': 'Internal server error'}
    }
)
def create_task(payload: DocumentCreate, current_user: CurrentUser, document_service: DependsDocumentService) -> ApiResponse:
    try:
        task_id = document_service.create_document(current_user.id, payload)
        return DocumentResponse(
            message=f'DocumentCollection-{task_id} created successfully'
        )
    except SQLAlchemyError as err:
        logger.error("document_collection creation failed", error=err, error_type="database error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error: {err}'
        ) from err
    except Exception as err:
        logger.error("document_collection creation failed", error=err, error_type="unexpected error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Unexpected error: {err}'
        ) from err


@router.put(
    '/{document_id}',
    response_model=DocumentResponse,
    summary='Update a document',
    description='Update an existing document by its ID',
    responses={
        200: {
            'description': 'Document updated successfully',
            'model': DocumentResponse
        },
        404: {'description': 'Document not found'},
        500: {'description': 'Internal server error'}
    }
)
def update_task(document_id: int, payload: DocumentUpdate, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentResponse:
    try:
        updated_task = document_service.update_document(user_id=current_user.id, document_id=document_id, doc_col_data=payload)

        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Document with ID {document_id} not found'
            )

        return DocumentResponse(message=f'DocumentCollection-{document_id} updated successfully')
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        logger.error("document update failed", error=err, error_type="database error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while updating DocumentCollection-{document_id}'
        ) from err
    except Exception as err:
        logger.error("document update failed", error=err, error_type="unexpected error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred'
        ) from err


@router.delete(
    '/{document_id}',
    summary='Delete a DocumentCollection',
    description='Delete a DocumentCollection by its ID',
    responses={
        200: {'description': 'Document deleted successfully'},
        404: {'description': 'Document not found'},
        500: {'description': 'Internal server error'}
    }
)
def delete_task(document_id: int, current_user: CurrentUser, document_service: DependsDocumentService) -> DocumentResponse:
    try:
        deleted = document_service.delete_collection(current_user.id, document_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Document-{document_id} not found'
            )

        return DocumentResponse(
            message=f'Document-{document_id} deleted successfully'
        )
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        logger.error("document_collection deletion failed", error=err, error_type="database error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while deleting task-{document_id}'
        ) from err
    except Exception as err:
        logger.error("document_collection deletion failed", error=err, error_type="unexpected error", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred'
        ) from err
