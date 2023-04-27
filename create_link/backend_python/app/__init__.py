from fastapi import FastAPI

from app.api import router


def create_app() -> FastAPI:
    app = FastAPI(title="Create Link App")
    app.include_router(router)

    @app.get("/health-check", include_in_schema=False)
    async def health_check() -> dict:
        return {"project": "create_link/backend_python"}

    return app
