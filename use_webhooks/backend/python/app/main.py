import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.linking import router as linking_router
from app.api.links import router as links_router
from app.api.webhooks import router as webhooks_router
from app.settings import get_settings


def create_app() -> FastAPI:
    logging.basicConfig(level=get_settings().log_level)

    app = FastAPI(title="Use Webhooks App")
    app.include_router(linking_router)
    app.include_router(links_router)
    app.include_router(webhooks_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health-check", include_in_schema=False)
    async def health_check() -> dict:
        return {"project": "use_webhooks/backend/python"}

    return app


app = create_app()
