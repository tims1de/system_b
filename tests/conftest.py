import os
import pytest
from httpx import ASGITransport, AsyncClient

# Устанавливаем режим тестирования до импорта настроек или приложения
os.environ["MODE"] = "TEST"

from app.main import create_app
from sqlalchemy import text
from app.storage.database import engine
from app.storage.models import Base


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    """Создание таблиц в тестовой БД один раз за сессию."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clear_db():
    """Очистка всех таблиц перед каждым тестом для изоляции."""
    async with engine.begin() as conn:
        # Для SQLite отключаем внешние ключи на время очистки, если нужно
        await conn.execute(text("DELETE FROM transactions"))
    yield


@pytest.fixture()
def app():
    """Create a fresh FastAPI application for each test."""
    return create_app()


@pytest.fixture()
async def client(app):
    """Async HTTP client for testing FastAPI endpoints."""
    # Для срабатывания lifespan в httpx/FastAPI
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac
