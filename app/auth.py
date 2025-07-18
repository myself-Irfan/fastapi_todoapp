from typing import Tuple
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import get_user_from_token, gen_user_tokens
from app.logger import get_logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/users/login')
logger = get_logger(__name__)


def get_cur_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get current user from JWT token
    :param token: JWT access token
    :param db: Database session
    :return: User object
    :raises HTTPException: If token is invalid or user not found
    """

    try:
        user_id = get_user_from_token(token, token_type='access')

        if not user_id:
            logger.warning('Invalid or expired token')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid/expired token',
                headers={
                    'WWW-Authenticate': 'Bearer'
                }
            )

        user = db.get(User, user_id)
        if not user:
            logger.warning(f'User-{user_id} not registered')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'User-{user_id} not registered',
                headers={
                    'WWW-Authenticate': 'Bearer'
                }
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


def refresh_access_token(refresh_token: str, db: Session) -> Tuple[str, str]:
    """
    Generate new access token from refresh token
    :param refresh_token: Valid refresh token
    :param db: Database session
    :return: (new_access_token, new_refresh_token)
    :raises HTTPException: If refresh token is invalid
    """

    user_id = get_user_from_token(refresh_token, token_type='refresh')
    if not user_id:
        logger.error('Invalid refresh token')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token'
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )

    return gen_user_tokens(user_id)