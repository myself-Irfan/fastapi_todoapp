import structlog.contextvars
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from app.auth.service import AuthenticationService
from app.logger import get_logger

logger = get_logger(__name__)


class LoggingContextMiddleware(BaseHTTPMiddleware):
    """
    middleware to set basic logging context vars for entire request lifecycle
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        structlog.contextvars.clear_contextvars()

        client_host = request.client.host if request.client else None
        forwarded_for = request.headers.get("x-forward-for")
        ip = forwarded_for.split(",")[0].strip() if forwarded_for else client_host

        structlog.contextvars.bind_contextvars(
            method =request.method,
            path=request.url.path,
            ip=ip
        )

        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
            try:
                user_id = AuthenticationService.get_user_from_token(token, token_type="access")
                if user_id:
                    structlog.contextvars.bind_contextvars(user_id=user_id)
            except Exception:
                logger.error("Error extracting user from token", exc_info=True)
                pass

        response = await call_next(request)

        structlog.contextvars.clear_contextvars()

        return response