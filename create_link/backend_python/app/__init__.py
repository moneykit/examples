from app.api import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
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
        return {"project": "create_link/backend_python"}

    return app
