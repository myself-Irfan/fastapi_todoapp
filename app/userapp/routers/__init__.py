from fastapi import APIRouter

from app.userapp.routers.register_user import router as register_router
from app.userapp.routers.login_user import router as login_router


router = APIRouter(
    prefix='/api/users',
    tags=['User APIs']
)
router.include_router(register_router)
router.include_router(login_router)