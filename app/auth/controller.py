from fastapi import APIRouter, status, HTTPException, Header, Depends

from app.auth.service import AuthenticationService, AuthenticationError
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
def refresh_user_access_token(db: DbSession, authorization: str = Header(...)) -> RefreshTokenResponse:
    """
    Refresh user access token using a valid refresh token
    """

    if not authorization.startswith("Bearer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Authorization header format'
        )

    refresh_token = authorization.removeprefix("Bearer").strip()

    try:
        new_access_token = AuthenticationService.refresh_access_token(refresh_token, db)

        return RefreshTokenResponse(
            message='Access token refreshed successfully',
            data=RefreshTokenData(
                access_token=new_access_token
            )
        )
    except AuthenticationError as auth_err:
        logger.error(f'Authentication error: {auth_err}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(auth_err)
        ) from auth_err
    except Exception as err:
        logger.error(f'Unexpected error during token refresh: {err}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred'
        ) from err