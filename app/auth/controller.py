from fastapi import APIRouter, status, HTTPException

from app.auth.service import AuthenticationService
from app.logger import get_logger
from app.auth.model import RefreshTokenResponse, RefreshTokenData
from app.database.core import DbSession

router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication APIs']
)
logger = get_logger(__name__)


@router.post(
    "/refresh-token",
    response_model=RefreshTokenResponse,
    summary='Refresh access token',
    description='Generate a new access token using a valid refresh token',
    responses={
        200: {
            'description': 'Access token refreshed successfully',
            'model': RefreshTokenResponse
        },
        400: {'description': 'Invalid or expired refresh token'},
        500: {'description': 'Internal server error'}
    }
)
def refresh_user_access_token(authorization: str, db: DbSession) -> RefreshTokenResponse:
    """
    Refresh user access token using a valid refresh token
    """

    if not authorization.startswith("Bearer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Authorization header format'
        )

    refresh_token = authorization.removeprefix("Bearer").strip()
    new_access_token = AuthenticationService.refresh_access_token(refresh_token, db)

    return RefreshTokenResponse(
        message='Access token refreshed successfully',
        data=RefreshTokenData(
            access_token=new_access_token
        )
    )