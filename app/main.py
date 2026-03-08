from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes import router
from app.config.settings import settings
from app.storage.database import engine
from app.storage.models import Base
from app.services.seed_service import seed_test_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: инициализация ресурсов"""
    # Создаем таблицы в БД при старте (для SQLite/DEV)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)    
    await seed_test_data(UnitOfWork())
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        lifespan=lifespan
    )
    application.include_router(router)
    return application


app = create_app()
