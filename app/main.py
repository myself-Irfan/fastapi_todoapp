from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.taskapp.task_routes import router as task_api_router
from app.userapp.user_routes import router as user_api_router
from app.userapp.user_views import router as user_view_router
from app.taskapp.task_views import router as task_view_router
from app.database import engine, Base
from app.validation_handler import ValidationErrorHandler


def create_app() -> FastAPI:
    app = FastAPI(
        title='Task Management App',
        description='A taskapp management App with JWT',
        version='1.0.0'
    )

    app.add_exception_handler(
        RequestValidationError,
        ValidationErrorHandler.handle_validation_error
    )

    return app

app = create_app()
app.mount('/static', StaticFiles(directory='static'), name='static')

Base.metadata.create_all(bind=engine)
app.include_router(user_api_router)
app.include_router(user_view_router)
app.include_router(task_api_router)
app.include_router(task_view_router)

# TODO: Need to finish
# TODO: DB creation and migration scripts
# TODO: crontab like job reminding user to do their taskapp
# TODO: add CI/CD