from fastapi import APIRouter

router = APIRouter()

from .routes import router as main_router
router.include_router(main_router)
