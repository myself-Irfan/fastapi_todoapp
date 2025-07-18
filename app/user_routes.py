from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.user_schemas import UserRegister, UserLogin, UserOut, ApiResponse, LoginResponse, TokenPair
from app.database import get_db
from app.models import User
from app.logger import get_logger
from app.security import hash_pwd, verify_pwd, gen_user_tokens

router = APIRouter(
    prefix='/api/users',
    tags=['User APIs']
)
logger = get_logger(__name__)


@router.post(
    '/register',
    response_model=ApiResponse,
    summary='Register an user',
    description='Take name, email and password to register an user',
    responses={
        201: {
            "description": 'User created successfully',
            'model': ApiResponse
        },
        400: {'description': 'Email already in use'},
        500: {'description': 'Internal server error'}
    }
)
def create_user(payload: UserRegister, db: Session = Depends(get_db)) -> ApiResponse:
    logger.info(f'Received payload: {payload}')

    try:
        existing_user = db.query(User).filter(User.email == payload.email).first()  # type: ignore
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email already in use'
            )

        hashed_pwd = hash_pwd(payload.password)
        new_user = User(
            name=payload.name,
            email=payload.email,
            hashed_pwd=hashed_pwd
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f'User registered: {new_user.id}')
        return ApiResponse(
            message=f'User-{new_user.id} registered successfully'
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
    finally:
        db.close()


@router.post(
    '/login',
    response_model=LoginResponse,
    summary='Logs in a user with credentials',
    description='Take credentials and return access and refresh token for successful login',
    responses={
        200: {
            'description': 'User successfully logged in',
            'model': LoginResponse
        },
        401: {'description': 'Invalid credentials'},
        500: {'description': 'Internal server error'}
    }
)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        user = db.query(User).filter(User.email == user_data.email).first()  # type: ignore

        if not user:
            raise HTTPException(
                status_code=401,
                detail='User not registered'
            )

        is_valid, needs_rehash = verify_pwd(user.hashed_pwd, user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail='Invalid credentials'
            )

        if needs_rehash:
            logger.info(f'Rehashing password for user {user.id}')
            try:
                new_hash = hash_pwd(user_data.password)
                user.hashed_pwd = new_hash
                db.commit()
                logger.info(f'Password rehashed successfully for user {user.id}')
            except Exception as rehash_err:
                logger.error(f'Password rehash failed for user {user.id}: {rehash_err}')
            finally:
                db.close()

        access_token, refresh_token = gen_user_tokens(user.id)

        return LoginResponse(
            message='Login successful',
            data=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f'Unexpected error during login: {err}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred'
        ) from err

