from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated

from app.database.core import DbSession
from app.entities.user import User
from app.auth.service import AuthenticationService
from app.logger import get_logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login')
logger = get_logger(__name__)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    """
    Get current user from JWT token
    :param token:
    :param db:
    :return:
    """

    try:
        user_id = AuthenticationService.get_user_from_token(
            token,
            token_type='access'
        )

        if not user_id:
            logger.warning('Invalid or expired token')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid/expired token',
                headers={'WWW-Authenticate': 'Bearer'}
            )

        user = db.get(User, user_id)
        if not user:
            logger.warning(f'User-{user_id} not found')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'User-{user_id} not found',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        return user
    except SQLAlchemyError as err:
        logger.error(f'Database error while fetching user: {err}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Database error'
        ) from err
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f'Unexpected error in get_cur_user: {err}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal server error'
        ) from err


CurrentUser = Annotated[User, Depends(get_current_user)]