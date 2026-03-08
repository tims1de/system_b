import os
import pytest
from httpx import ASGITransport, AsyncClient

os.environ["MODE"] = "TEST"

from app.main import create_app
from app.storage.database import engine
from app.storage.models import Base
from app.storage.unit_of_work import UnitOfWork


@pytest.fixture(autouse=True)
async def init_db():
    """Очистка и создание таблиц в тестовой БД перед КАЖДЫМ тестом."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture()
def app():
    """Create a fresh FastAPI application for each test."""
    return create_app()


@pytest.fixture()
async def client(app):
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture()
async def uow():
    """Фикстура для UnitOfWork, готового к использованию."""
    async with UnitOfWork() as uow_obj:
        yield uow_obj
