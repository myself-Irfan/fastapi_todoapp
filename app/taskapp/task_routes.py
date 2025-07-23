from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.auth import get_cur_user
from app.taskapp.task_schemas import TaskCreate, TaskRead, TaskListResponse, TaskResponse, TaskUpdate, ApiResponse
from app.database import get_db
from app.models import Task
from app.logger import get_logger

router = APIRouter(
    prefix="/api/tasks",
    tags=["Task APIs"],
    dependencies=[Depends(get_cur_user)]
)
logger = get_logger(__name__)


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
def get_all_tasks(db: Session = Depends(get_db)) -> TaskListResponse:
    """
    Retrieve all tasks from the database.
    Args: db: SQLAlchemy database session
    Returns: TaskListResponse containing list of tasks
    Raises: HTTPException: If database operation fails
    """
    logger.info("Fetching all tasks")

    try:
        tasks = db.query(Task).all()
        logger.info(f"Retrieved {len(tasks)} tasks")

        if tasks:
            task_data = [TaskRead.model_validate(task) for task in tasks]
            return TaskListResponse(
                message="Tasks retrieved successfully",
                data=task_data
            )
        else:
            return TaskListResponse(
                message="No taskapp found",
                data=[]
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
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Retrieve a specific taskapp by its ID.
    Args: task_id: The ID of the taskapp to retrieve, db: SQLAlchemy database session
    Returns: TaskResponse containing the taskapp data
    Raises: HTTPException: If taskapp not found or database operation fails
    """
    logger.info(f'Fetching taskapp with ID: {task_id}')

    try:
        task = db.get(Task, task_id)

        if not task:
            logger.warning(f'Task with ID {task_id} not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with ID {task_id} not found'
            )

        task_data = TaskRead.model_validate(task)
        logger.info(f'Retrieved taskapp: {task.title}')
        return TaskResponse(
            message='Task retrieved successfully',
            data=task_data
        )
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        logger.error(f'Database error while fetching taskapp: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while fetching taskapp-{task_id}'
        ) from err
    except Exception as err:
        logger.error(f'Unexpected error: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An unexpected error occured'
        ) from err


@router.post(
    "/",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new taskapp',
    description='Add a new taskapp to database',
    responses={
        201: {
            'description': 'Task created',
            'model': ApiResponse
        },
        500: {'description': 'Internal server error'}
    }
)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> ApiResponse:
    """
    Create a new taskapp in the database.
    Args: payload: TaskCreate schema with taskapp data, db: SQLAlchemy database session
    Returns: Dictionary with success message
    Raises: HTTPException: If database operation fails
    """
    try:
        logger.info(f'Creating new taskapp with title-{payload.title}')

        task = Task(**payload.model_dump())
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info(f'Created taskapp: {task.id}')
        return TaskResponse(
            message=f'Task-{task.id} created successfully'
        )
    except SQLAlchemyError as err:
        db.rollback()
        logger.error(f'Database error: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error: {err}'
        ) from err
    except Exception as err:
        db.rollback()
        logger.error(f'Unexpected error: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Unexpected error: {err}'
        ) from err

@router.put(
    '/{task_id}',
    response_model=TaskResponse,
    summary='Update a taskapp',
    description='Update an existing taskapp by its ID',
    responses={
        200: {
            'description': 'Task updated successfully',
            'model': TaskResponse
        },
        404: {'description': 'Task not found'},
        500: {'description': 'Internal server error'}
    }
)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Update an existing taskapp by its ID.
    Args: task_id: The ID of the taskapp to update, payload: TaskUpdate schema with updated taskapp data, db: SQLAlchemy database session
    Returns: TaskResponse containing the updated taskapp data
    Raises: HTTPException: If taskapp not found or database operation fails
    """
    logger.info(f'Fetching taskapp-{task_id} for update')

    try:
        task = db.get(Task, task_id)

        if not task:
            logger.warning(f'Task with ID {task_id} not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with ID {task_id} not found'
            )

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        db.commit()
        db.refresh(task)

        return TaskResponse(message=f'Task-{task_id} updated successfully')
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        db.rollback()
        logger.error(f'Database error while updating taskapp: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while updating taskapp-{task_id}'
        ) from err
    except Exception as err:
        db.rollback()
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
def delete_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Delete a taskapp by its ID.
    Args: task_id: The ID of the taskapp to delete, db: SQLAlchemy database session
    Returns: Dictionary with success message
    Raises: HTTPException: If taskapp not found or database operation fails
    """
    try:
        logger.info(f'Deleting taskapp-{task_id}')

        task = db.get(Task, task_id)

        if not task:
            logger.warning(f'Task with ID {task_id} not found for deletion')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with ID {task_id} not found'
            )

        db.delete(task)
        db.commit()
        logger.info('Task deleted')
        return TaskResponse(
            message=f'Task-{task_id} deleted successfully'
        )
    except HTTPException:
        raise
    except SQLAlchemyError as err:
        db.rollback()
        logger.error(f'Database error while deleting taskapp: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error while deleting taskapp-{task_id}'
        ) from err
    except Exception as err:
        db.rollback()
        logger.error(f'Unexpected error while deleting taskapp: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred'
        ) from err
