from fastapi.routing import APIRouter

from .budget import router as budget_router
from .linking import router as linking_router
from .links import router as links_router
from .login import router as login_router
from .webhooks_handler import router as webhook_router

router = APIRouter()
router.include_router(budget_router)
router.include_router(linking_router)
router.include_router(links_router)
router.include_router(login_router)
router.include_router(webhook_router)
