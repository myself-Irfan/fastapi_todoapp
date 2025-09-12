from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.auth.dependencies import get_current_user
from app.taskapp.model import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate, ApiResponse
from app.database.core import DbSession
from app.logger import get_logger
from app.taskapp.service import TaskService

router = APIRouter(
    prefix="/api/tasks",
    tags=["Task APIs"],
    dependencies=[Depends(get_current_user)]
)
logger = get_logger(__name__)

def get_task_service(db: DbSession) -> TaskService:
    """
    Dependency to get TaskService instance with database session.
    Args: db: SQLAlchemy database session
    Returns: TaskService instance
    """
    return TaskService(db=db)


@router.get(
    "/",
    response_model=TaskListResponse,
    summary="Get all tasks",
    description="Retrieve all tasks from the database",
    responses={
        200: {
            "description": "Tasks retrieved successfully",
            "model": TaskListResponse
        },
        500: {"description": "Internal server error"}
    }
)
def get_all_tasks(task_service: TaskService = Depends(get_task_service)) -> TaskListResponse:
    """
    Retrieve all tasks from the database.
    Args: task_service: TaskService dependency
    Returns: TaskListResponse containing list of tasks
    Raises: HTTPException: If database operation fails
    """
    logger.info("Fetching all tasks")

    try:
        tasks = task_service.fetch_tasks()

        message = "Tasks retrieved successfully" if tasks else "No tasks found"

        return TaskListResponse(
            message=message,
            data=tasks or []
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching tasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching tasks"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while fetching tasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) from e


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary='Get taskapp by ID',
    description='Retrieve a specific taskapp by its ID',
    responses={
        200: {
            'description': 'Task retrieved successfully',
            'model': TaskResponse
        },
        404: {'description': 'Task not found'},
        500: {'description': 'Internal server error'}
    }
)
def get_task(task_id: int, task_service: TaskService = Depends(get_task_service)) -> TaskResponse:
    """
    Retrieve a specific taskapp by its ID.
    Args: task_id: The ID of the taskapp to retrieve, db: SQLAlchemy database session
    Returns: TaskResponse containing the taskapp data
    Raises: HTTPException: If taskapp not found or database operation fails
    """
    logger.info(f'Fetching task with ID: {task_id}')

    try:
        task = task_service.fetch_task_by_id(task_id)

        if not task:
            logger.warning(f'Task with ID {task_id} not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with ID {task_id} not found'
            )

        logger.info(f'Retrieved task: {task.title}')
        return TaskResponse(
            message='Task retrieved successfully',
            data=task
        )
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        logger.error(f'Database error while fetching task: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while fetching task-{task_id}'
        ) from err
    except Exception as err:
        logger.error(f'Unexpected error: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An unexpected error occurred'
        ) from err


@router.post(
    "/",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new task object',
    description='Add a new object to tasklist table database',
    responses={
        201: {
            'description': 'Task created',
            'model': ApiResponse
        },
        500: {'description': 'Internal server error'}
    }
)
def create_task(payload: TaskCreate, task_service: TaskService = Depends(get_task_service)) -> ApiResponse:
    """
    Create a new task in the database.
    Args: payload: TaskCreate schema with task data, task_service: TaskService dependency
    Returns: TaskResponse containing success message
    Raises: HTTPException: If database operation fails
    """
    try:
        logger.info(f'Request received to create taskapp: {payload.title}')

        task_id = task_service.create_task(payload)
        return TaskResponse(
            message=f'Task-{task_id} created successfully'
        )
    except SQLAlchemyError as err:
        logger.error(f'Database error: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error: {err}'
        ) from err
    except Exception as err:
        logger.error(f'Unexpected error: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Unexpected error: {err}'
        ) from err


@router.put(
    '/{task_id}',
    response_model=TaskResponse,
    summary='Update a task',
    description='Update an existing task by its ID',
    responses={
        200: {
            'description': 'Task updated successfully',
            'model': TaskResponse
        },
        404: {'description': 'Task not found'},
        500: {'description': 'Internal server error'}
    }
)
def update_task(task_id: int, payload: TaskUpdate, task_service: TaskService = Depends(get_task_service)) -> TaskResponse:
    """
    Update an existing taskapp by its ID.
    Args: task_id: The ID of the taskapp to update, payload: TaskUpdate schema with updated taskapp data, db: SQLAlchemy database session
    Returns: TaskResponse containing the updated taskapp data
    Raises: HTTPException: If taskapp not found or database operation fails
    """
    logger.info(f'Received update request for task-{task_id}')

    try:
        updated_task = task_service.update_task(task_id, payload)

        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with ID {task_id} not found'
            )

        return TaskResponse(message=f'Task-{task_id} updated successfully')
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        logger.error(f'Database error while updating taskapp: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while updating taskapp-{task_id}'
        ) from err
    except Exception as err:
        logger.error(f'Unexpected error while updating taskapp: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred'
        ) from err


@router.delete(
    '/{task_id}',
    summary='Delete a taskapp',
    description='Delete a taskapp by its ID',
    responses={
        200: {'description': 'Task deleted successfully'},
        404: {'description': 'Task not found'},
        500: {'description': 'Internal server error'}
    }
)
def delete_task(task_id: int, task_service: TaskService = Depends(get_task_service)) -> TaskResponse:
    """
    Delete a taskapp by its ID.
    Args: task_id: The ID of the taskapp to delete, db: SQLAlchemy database session
    Returns: Dictionary with success message
    Raises: HTTPException: If taskapp not found or database operation fails
    """
    logger.info(f'Deleting taskapp-{task_id}')

    try:
        deleted = task_service.delete_task(task_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task-{task_id} not found'
            )

        logger.info('Task deleted')
        return TaskResponse(
            message=f'Task-{task_id} deleted successfully'
        )
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        logger.error(f'Database error while deleting task: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while deleting task-{task_id}'
        ) from err
    except Exception as err:
        logger.error(f'Unexpected error while deleting task: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred'
        ) from err
