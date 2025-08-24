from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from app.auth.service import AuthenticationService
from app.userapp.model import UserRegister, UserLogin, ApiResponse, LoginResponse, LoginTokenData
from app.database.core import DbSession
from app.logger import get_logger
from app.userapp.service import UserService

router = APIRouter(
    prefix='/api/users',
    tags=['User APIs']
)
logger = get_logger(__name__)

def get_user_service(db: DbSession) -> UserService:
    """
    Dependency to get UserService instance with database session.
    Args: db: SQLAlchemy database session
    Returns: UserService instance
    """
    return UserService(db=db)


@router.post(
    '/register',
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
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
def register_user(payload: UserRegister, user_service: UserService = Depends(get_user_service)) -> ApiResponse:
    logger.info(f'Received payload: {payload}')

    try:
        user = user_service.create_registered_user(payload)

        if user is None:
            raise ValueError('Email already in use')

        return ApiResponse(
            message=f'User-{user.id} created successfully',
        )
    except ValueError as val_err:
        logger.warning(f'Validation error: {val_err}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        ) from val_err
    except (OperationalError, SQLAlchemyError) as db_err:
        logger.error(f'Database error: {db_err}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Database error: {db_err}'
        ) from db_err
    except Exception as err:
        logger.error(f'Unexpected error during user creation: {err}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred'
        ) from err


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
def login_user(user_data: UserLogin, user_service: UserService = Depends(get_user_service)) -> LoginResponse:
    try:
        user = user_service.login_user(user_data.email, user_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        access_token = AuthenticationService.generate_access_token(user.id)
        refresh_token = AuthenticationService.generate_refresh_token(user.id)

        return LoginResponse(
            message="Login successful",
            data=LoginTokenData(access_token=access_token, refresh_token=refresh_token),
        )
    except HTTPException as http_err:
        raise http_err
    except (OperationalError, SQLAlchemyError) as db_err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(db_err))
    except Exception as err:
        logger.error(f"Unexpected error during login: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error")
