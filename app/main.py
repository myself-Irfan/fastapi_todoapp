from fastapi import FastAPI
from app.task_routes import router as task_api_router
from app.task_views import router as task_view_router
from app.auth_routes import router as auth_router
from app.database import engine, Base
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="Task Management API",
    description="A task management API with JWT authentication",
    version="1.0.0"
)

app.mount('/static', StaticFiles(directory='static'), name='static')

Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(task_api_router)
app.include_router(task_view_router)

# TODO: Use HTMX? If not possible use HTML + JS
# TODO: Need to finish
# TODO: DB creation and migration scripts
# TODO: JSON API response