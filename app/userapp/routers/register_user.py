from fastapi import APIRouter, status, Request, HTTPException

from app.rate_limiter import limiter
from app.config import settings
from app.userapp.dependencies import DependsUserService
from app.logger import get_logger
from app.userapp.model import UserRegister, ApiResponse
from app.userapp.exceptions import UserOperationException

router = APIRouter()

logger = get_logger(__name__)


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
@limiter.limit(f"{settings.register_limit_per_hour}/hour")
def register_user(request: Request, payload: UserRegister, user_service: DependsUserService) -> ApiResponse:
    try:
        user = user_service.create_registered_user(payload)
        return ApiResponse(
            message=f'User-{user.id} created successfully',
        )
    except UserOperationException as e:
        logger.error(f'User registration operation failed: {e.message}')
        raise HTTPException(status_code=e.status_code, detail=e.message)
