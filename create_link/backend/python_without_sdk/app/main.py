import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.settings import get_settings


def create_app() -> FastAPI:
    logging.basicConfig(level=get_settings().log_level)
    app = FastAPI(title="Create Link App")
    app.include_router(router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health-check", include_in_schema=False)
    async def health_check() -> dict:
        return {"project": "create_link/backend/python_without_sdk"}

    return app


app = create_app()
