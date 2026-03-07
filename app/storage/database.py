from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config.settings import settings

# Создаем асинхронный движок
engine = create_async_engine(
    settings.url,
    echo=False,  # Можно включить True для отладки SQL запросов
    future=True
)

# Фабрика асинхронных сессий
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    """Генератор асинхронных сессий для внедрения зависимостей"""
    async with async_session_factory() as session:
        yield session
