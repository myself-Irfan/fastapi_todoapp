from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError, HashingError
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Optional
from fastapi import HTTPException, status

from app.config import settings
from app.database.core import DbSession
from app.userapp.entities import DocumentUser
from app.logger import get_logger

_pwd_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

logger = get_logger(__name__)

class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthenticationService:
    """Service class for authentication-related operations."""

    @staticmethod
    def hash_pwd(pwd_str: str) -> str:
        """
        Hash a password using argon2.
        :param pwd_str: Plain text password
        :return: Hashed password string
        :raises ValueError: If password is empty
        :raises AuthenticationError: If hashing fails
        """
        if not pwd_str or not pwd_str.strip():
            raise ValueError('Password cannot be empty')

        try:
            return _pwd_hasher.hash(pwd_str)
        except HashingError as err:
            logger.error(f'Password hashing failed: {err}')
            raise AuthenticationError(f'Password hashing failed: {err}') from err

    @staticmethod
    def verify_pwd(pwd_hashed: str, pwd_str: str) -> tuple[bool, bool]:
        """
        Verify password and check if rehash is needed.
        :param pwd_hashed: Hashed password from database
        :param pwd_str: Plain text password
        :return: (is_valid, needs_rehash)
        """
        try:
            if _pwd_hasher.verify(pwd_hashed, pwd_str):
                need_rehash = _pwd_hasher.check_needs_rehash(pwd_hashed)
                if need_rehash:
                    logger.info('Password needs rehash')
                return True, need_rehash
        except VerifyMismatchError as ver_err:
            logger.warning(f'Verify mismatch error: {ver_err}')
        except InvalidHashError as invalid_err:
            logger.error(f'Invalid hash error: {invalid_err}')
        except Exception as err:
            logger.error(f'Unexpected error: {err}')

        return False, False

    @staticmethod
    def _create_jwt(user_id: int, expires_delta: timedelta, token_type: str) -> str:
        """
            Create a JWT token
            :param data: Data to encode in token
            :param expires_delta: Token expiration time
            :param token_type: Type of token ('access' or 'refresh')
            :return: JWT token
            :raises AuthError: If token creation fails
            """

        if user_id <= 0:
            raise ValueError(f'Invalid user_id: {user_id}')

        if token_type not in ['access', 'refresh']:
            raise ValueError('Token type must be access or refresh')

        try:
            now = datetime.now(timezone.utc)
            payload = {
                'sub': str(user_id),
                'type': token_type,
                'iat': now,
                'exp': now + expires_delta
            }
            return jwt.encode(
                payload,
                settings.secret_key,
                algorithm=settings.algorithm
            )
        except Exception as err:
            logger.error(f'{token_type} Token creation failed: {err}')
            raise AuthenticationError(f'Failed to create {token_type} token: {err}') from err

    @classmethod
    def generate_access_token(cls, user_id: int) -> str:
        """
            generate access token
            :param user_id: int
            :return: access_token -> str
            """
        return cls._create_jwt(
            user_id=user_id,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
            token_type='access'
        )

    @classmethod
    def generate_refresh_token(cls, user_id: int) -> str:
        """
            generate refresh token
            :param user_id: int
            :return: refresh_token -> str
            """
        return cls._create_jwt(
            user_id=user_id,
            expires_delta=timedelta(minutes=settings.refresh_token_expire_days),
            token_type='refresh'
        )

    @staticmethod
    def verify_token(token: str, expected_type: str) -> Optional[dict]:
        """
        Verify a JWT token and return its payload if valid.
        :param token:
        :param expected_type:
        :return:
        """

        if not token or not isinstance(token, str):
            logger.warning(f'Invalid token input: {"missing" if not token else "not a string"}')
            return None

        if not expected_type:
            logger.warning('Expected token type is required')
            return None

        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )

            if not payload.get('sub'):
                logger.warning('Token payload missing subject (sub)')
                return None

            if payload.get('type') != expected_type:
                logger.warning(f'Token type mismatch: expected {expected_type}, got {payload.get("type")}')
                return None

            logger.info('Token verified successfully')
            return payload
        except JWTError as jwt_err:
            logger.error(f"Token verification failed: {jwt_err}")
            return None
        except Exception as err:
            logger.error(f"Unexpected error during token verification: {err}")
            return None

    @classmethod
    def get_user_from_token(cls, token: str, token_type: str) -> Optional[int]:
        """
        Extract user ID from a JWT token.
        :param token: JWT token
        :param token_type: Token type to verify
        :return: User ID or None if token is invalid
        """
        payload = cls.verify_token(token, token_type)

        if not payload:
            logger.warning('Payload not found')
            return None

        try:
            user_id_str = payload.get('sub')
            if not user_id_str:
                logger.warning('Token missing user_id')
                return None

            user_id = int(user_id_str)
            if user_id <= 0:
                logger.warning('Invalid user_id in token')
                raise ValueError

            return user_id
        except (ValueError, TypeError) as err:
            logger.warning(f'Invalid user ID format in token: {err}')
            return None

    @classmethod
    def refresh_access_token(cls, refresh_token: str, db: DbSession) -> str:
        """
        Generate a new access token from a valid refresh token.
        :param refresh_token: Valid refresh token
        :param db: Database session
        :return: New access token
        :raises AuthenticationError: If refresh token is invalid
        """
        user_id = cls.get_user_from_token(refresh_token, 'refresh')
        if not user_id:
            logger.error('Invalid refresh token')
            raise AuthenticationError('Invalid refresh token')

        user = db.get(DocumentUser, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'User-{user_id} not found',
            )

        return cls.generate_access_token(user_id)
