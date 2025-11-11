from fastapi.params import Depends
from typing import Annotated

from app.database.core import DbSession
from app.userapp.service import UserService

def get_user_service(db: DbSession) -> UserService:
    """
    Dependency to get UserService instance with database session.
    Args: db: SQLAlchemy database session
    Returns: UserService instance
    """
    return UserService(db=db)

DependsUserService = Annotated[UserService, Depends(get_user_service)]