from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter(
    prefix='',
    tags=['User Views']
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory='templates')


@router.get('/register', response_class=HTMLResponse)
def render_register(request: Request):
    """
    render register user page
    :param request:
    :return:
    """
    return templates.TemplateResponse('register.html', {'request': request})