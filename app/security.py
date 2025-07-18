from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError, HashingError
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.logger import get_logger
from app.config import settings

_pwd_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

logger = get_logger(__name__)


class AuthError(Exception):
    pass


def hash_pwd(pwd_str: str) -> str:
    """
    Hash a password using argon2
    :param pwd_str: Plain text password
    :return: hashed password str
    :raises ValueError: If password is empty
    :raises AuthError: If hashing fails
    """
    if not pwd_str or not pwd_str.strip():
        raise ValueError('Password can not be empty')

    try:
        return _pwd_hasher.hash(pwd_str)
    except HashingError as err:
        logger.error(f'Password hashing failed: {err}')
        raise AuthError(f'Password hashing failed: {err}') from err


def verify_pwd(pwd_hashed: str, pwd_str: str) -> tuple[bool, bool]:
    """
    Verify password and check if rehash is needed
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


def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    """
    Create a JWT token
    :param data: Data to encode in token
    :param expires_delta: Token expiration time
    :param token_type: Type of token ('access' or 'refresh')
    :return: JWT token
    :raises AuthError: If token creation fails
    """

    if not data or not isinstance(data, dict):
        raise ValueError('Data must be a non-empty dictionary')

    if token_type not in ['access', 'refresh']:
        raise ValueError('Token type must be access or refresh')

    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({
            'exp': expire,
            'iat': datetime.now(timezone.utc),
            'type': token_type
        })
        return jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
    except Exception as err:
        logger.error(f'{token_type} Token creation failed: {err}')
        raise RuntimeError(f'Failed to create {token_type} token: {err}') from err


def gen_user_tokens(user_id: int) -> tuple[str, str]:
    """
    Generate access and refresh tokens for user
    :param user_id: User ID
    :return: (access_token, refresh_token)
    :raises ValueError: If user_id is invalid
    :raises AuthError: If token generation fails
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError('User ID must be a positive integer')

    payload = {'sub': str(user_id)}

    logger.info(f'Creating access token')
    access_token = _create_token(
        data=payload,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type='access'
    )

    logger.info(f'Creating refresh token')
    refresh_token = _create_token(
        data=payload,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        token_type='refresh'
    )

    return access_token, refresh_token


def verify_token(token: str, expected_type: str) -> dict | None:
    """
    Verify and decode JWT token
    :param token: JWT token
    :param expected_type: Expected token type ('access' or 'refresh')
    :return: Token payload or None if invalid
    """

    if not token:
        logger.warning('Token not received')
        return None

    if not isinstance(token, str):
        logger.warning('Invalid token format')
        return None

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        if not payload.get('sub'):
            logger.warning('Token missing sub')
            return None

        if payload.get('type') != expected_type:
            logger.warning(f'Token type mismatch: expected {expected_type}')
            return None

        logger.info('Token verified')
        return payload
    except JWTError as err:
        logger.error(f'Token verification failed: {err}')
        return None
    except Exception as err:
        logger.error(f'Unexpected error during token verification: {err}')
        return None


def get_user_from_token(token: str, token_type: str = 'access') -> int | None:
    """
    Extract user ID from token
    :param token: JWT token
    :param token_type: Token type to verify
    :return: User ID or None if invalid
    """
    payload = verify_token(token, token_type)

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
            return None

        return user_id
    except (ValueError, TypeError) as err:
        logger.warning(f'Invalid user ID format in token: {err}')
        return None