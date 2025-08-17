from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List

from app.logger import get_logger
from app.entities.task import Task
from app.taskapp.model import TaskRead, TaskCreate, TaskUpdate

logger = get_logger(__name__)


class TaskService:
    """
    Service class for task operations.
    This class contains methods to interact with the task database.
    """
    def __init__(self, db: Session):
        self.db = db

    def fetch_tasks(self) -> List[TaskRead]:
        """
        Fetch all tasks from the database.
        :return: List of Task objects or None if no tasks found
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            tasks = self.db.query(Task).all()
            logger.info(f'Fetched {len(tasks)} tasks from the database')

            return [TaskRead.model_validate(task) for task in tasks]
        except SQLAlchemyError as sql_err:
            logger.error(f'Database error: {sql_err}', exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}", exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e

    def fetch_task_by_id(self, task_id: int) -> TaskRead | None:
        """
        Fetch a specific task by its ID.
        :param task_id: The ID of the task to fetch
        :return: TaskRead object containing task data
        :raises SQLAlchemyError: If database operation fails
        """
        try:
            task = self.db.get(Task, task_id)

            if not task:
                logger.warning(f'Task with ID {task_id} not found')
                return None

            logger.info(f'Fetched task with ID {task_id}')
            return TaskRead.model_validate(task)
        except SQLAlchemyError as sql_err:
            logger.error(f'Database error while fetching task {task_id}: {sql_err}', exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}", exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e

    def create_task(self, task_data: TaskCreate) -> int:
        """
        Create a new task in the database.
        :param task_data: TaskRead object containing task data
        :return: ID of the created task
        :raises SQLAlchemyError: If database operation fails
        """
        logger.info(f'Creating new task with title: {task_data.title}')

        try:
            new_task = Task(**task_data.model_dump())
            self.db.add(new_task)
            self.db.commit()
            self.db.refresh(new_task)

            logger.info(f'Created new task with ID {new_task.id}')
            return new_task.id
        except SQLAlchemyError as sql_err:
            self.db.rollback()
            logger.error(f'Database error while creating task: {sql_err}', exc_info=True)
            raise SQLAlchemyError(f"Database error while creating task: {sql_err}") from sql_err
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating task: {e}", exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e

    def update_task(self, task_id: int, task_data: TaskUpdate) -> int | None:
        """
        update an existing task in the database.
        :param task_id: id of the task to update
        :param task_data: TaskUpdate object containing updated task data
        :return: task_id of the updated task or None if task not found
        """

        logger.info(f'Updating task with ID {task_id}')

        try:
            task = self.db.get(Task, task_id)

            if not task:
                logger.warning(f'Task with ID {task_id} not found')
                return None

            for key, value in task_data.model_dump(exclude_unset=True).items():
                setattr(task, key, value)

            self.db.commit()
            self.db.refresh(task)

            logger.info(f'Updated task with ID-{task.id}')
            return task.id
        except SQLAlchemyError as sql_err:
            logger.error(f'Database error while updating task {task_id}: {sql_err}', exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}", exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.
        :param task_id: The ID of the task to delete
        :raises SQLAlchemyError: If database operation fails
        :raises ValueError: If task with given ID does not exist
        """
        logger.info(f'Deleting task with ID {task_id}')

        try:
            task = self.db.get(Task, task_id)

            if not task:
                logger.warning(f'Task with ID {task_id} not found')
                return False

            self.db.delete(task)
            self.db.commit()

            logger.info(f'Deleted task with ID {task_id}')
            return True
        except SQLAlchemyError as sql_err:
            logger.error(f'Database error while deleting task {task_id}: {sql_err}', exc_info=True)
            raise sql_err
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
            raise SQLAlchemyError(f"Unexpected database error: {str(e)}") from e