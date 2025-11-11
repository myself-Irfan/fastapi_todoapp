from fastapi import APIRouter, HTTPException

from app.userapp.model import UserLogin, LoginResponse, LoginTokenData
from app.userapp.dependencies import DependsUserService
from app.logger import get_logger
from app.userapp.exceptions import UserOperationException


router = APIRouter()

logger = get_logger(__name__)


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
def login_user(user_data: UserLogin, user_service: DependsUserService) -> LoginResponse:
    try:
        access_token,  refresh_token = user_service.login_user(user_data.email, user_data.password)

        return LoginResponse(
            message="Login successful",
            data=LoginTokenData(access_token=access_token, refresh_token=refresh_token),
        )
    except UserOperationException as e:
        logger.error(f'User operation failed: {e.message}')
        raise HTTPException(status_code=e.status_code, detail=e.message)
