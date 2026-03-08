from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.storage.models import Base, TransactionModel

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Базовый абстрактный репозиторий"""
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def add(self, entity: T) -> None:
        """Добавить сущность в сессию"""
        self.session.add(entity)

    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Получить по первичному ключу"""
        return await self.session.get(self.model, entity_id)

    async def list_all(self) -> List[T]:
        """Получить все записи"""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())


class TransactionRepository(BaseRepository):
    """Репозиторий для работы с транзакциями"""
    def __init__(self, session: AsyncSession):
        super().__init__(TransactionModel, session)

    async def get_by_hash(self, tx_hash: str):
        """Поиск транзакции по хэшу"""
        stmt = select(self.model).where(self.model.hash == tx_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_filtered(self, start_date, end_date, limit=100, offset=0):
        """Фильтрация транзакций для эндпоинта outgoing"""
        stmt = (
            select(self.model)
            .where(self.model.transaction_time.between(start_date, end_date))
            .limit(limit)
            .offset(offset)
            .order_by(self.model.transaction_time.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
