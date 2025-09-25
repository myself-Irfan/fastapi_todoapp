import json
from typing import Optional, Any, Union
import structlog.contextvars
from fastapi import Request
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, StreamingResponse
from starlette.types import ASGIApp

from app.auth.service import AuthenticationService
from app.logger import get_logger

logger = get_logger(__name__)


class LoggingContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set logging context vars for entire request lifecycle
    and log request/response payloads.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        structlog.contextvars.clear_contextvars()

        structlog.contextvars.bind_contextvars(
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params) if request.query_params else None
        )

        await self.__bind_user_context(request)
        await self.__bind_ip_context(request)

        request_body = await self.__get_request_body(request)

        logger.info(
            "Request started",
            payload=request_body,
            headers=dict(request.headers),
        )

        try:
            response = await call_next(request)

            if isinstance(response, StreamingResponse) and not isinstance(response, Response):
                logger.info(
                    "Request finished (streaming response)",
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                return response

            response_body = await self.__get_response(response)

            logger.info(
                "Request finished",
                payload=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

            return response

        except Exception as e:
            logger.error(
                "Request failed with exception",
                exception=str(e),
                exc_info=True,
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()

    @staticmethod
    async def __bind_user_context(request: Request) -> None:
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
            try:
                user_id = AuthenticationService.get_user_from_token(token, token_type="access")
                if user_id:
                    structlog.contextvars.bind_contextvars(user_id=user_id)
            except Exception:
                logger.error("Error extracting user from token", exc_info=True)

    @staticmethod
    async def __bind_ip_context(request: Request) -> None:
        client_host = request.client.host if request.client else None
        forwarded_for = request.headers.get("x-forwarded-for")

        structlog.contextvars.bind_contextvars(
            ip=forwarded_for.split(",")[0].strip() if forwarded_for else client_host
        )

    @staticmethod
    async def __get_request_body(request: Request) -> Optional[Any]:
        """Safely extract and parse request body"""
        try:
            body = await request.body()
            if not body:
                return None

            text = body.decode("utf-8")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

        except Exception as e:
            logger.warning("Failed to read request body", error=str(e))
            return None

    async def __get_response(self, response: Response) -> Optional[Union[str, dict]]:
        try:
            body = b"".join([chunk async for chunk in response.body_iterator])
            decoded = self.__decode_body(body)

            response.body_iterator = iterate_in_threadpool(iter([body]))
            return decoded
        except Exception as e:
            logger.warning("Failed to read response body", error=str(e))
            return None

    def __decode_body(self, body: bytes) -> Optional[Union[str, dict]]:
        if not body:
            return None
        try:
            text = body.decode("utf-8")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
        except Exception:
            return None