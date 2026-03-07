from fastapi import FastAPI

from app.api.routes import router
from app.config.settings import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
    )
    application.include_router(router)
    return application

app = create_app()
