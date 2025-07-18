from fastapi import FastAPI
from app.task_routes import router as task_api_router
from app.user_routes import router as user_api_router
from app.task_views import router as task_view_router
from app.database import engine, Base
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title='Task Management App',
    description='A task management App with JWT',
    version='1.0.0'
)

app.mount('/static', StaticFiles(directory='static'), name='static')

Base.metadata.create_all(bind=engine)
app.include_router(user_api_router)
app.include_router(task_api_router)
app.include_router(task_view_router)

# TODO: use HTML + JS
# TODO: Need to finish
# TODO: DB creation and migration scripts
# TODO: JSON API response
# TODO: User register and Login using JWT
# TODO: crontab like job reminding user to do their task