from fastapi import FastAPI

from budgeting_app.api import router


def create_app() -> FastAPI:
    app = FastAPI(title="Budgeting App")
    app.include_router(router)

    @app.get("/health-check", include_in_schema=False)
    async def health_check() -> dict:
        return {"project": "budgeting_app/backend_python"}

    return app
