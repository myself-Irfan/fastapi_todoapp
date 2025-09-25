from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.auth.controller import router as auth_api_router
from app.middleware.logging_context import LoggingContextMiddleware
from app.taskapp.controller import router as task_api_router
from app.userapp.controller import router as user_api_router
from app.userapp.view import router as user_view_router
from app.taskapp.task_views import router as task_view_router
from app.database.core import engine, Base
from app.validation_handler import ValidationErrorHandler
from app.logger import configure_logger


configure_logger()

def create_app() -> FastAPI:
    app = FastAPI(
        title='Task Management App',
        description='A taskapp management App with JWT',
        version='1.0.0',
        docs_url='/docs',
        redoc_url='/redoc'
    )

    app.add_middleware(LoggingContextMiddleware)

    app.add_exception_handler(
        RequestValidationError,
        ValidationErrorHandler.handle_validation_error
    )

    return app

app = create_app()
app.mount('/static', StaticFiles(directory='static'), name='static')

Base.metadata.create_all(bind=engine)

app.include_router(auth_api_router)
app.include_router(user_api_router)
app.include_router(user_view_router)
app.include_router(task_api_router)
app.include_router(task_view_router)

# TODO: mask sensitive field
# TODO: log request response to table
# TODO: crontab to remind users for missed task