from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.storage.database import async_session_factory
from app.storage.repository import TransactionRepository


class UnitOfWork:
    """
    Паттерн Unit of Work для управления транзакциями.
    Обеспечивает атомарность операций.
    """
    def __init__(self):
        self._session_factory = async_session_factory
        self.session: Optional[AsyncSession] = None
        
        # Репозитории
        self.transactions: Optional[TransactionRepository] = None

    async def __aenter__(self):
        """Вход в контекстный менеджер: создание сессии и репозиториев"""
        self.session = self._session_factory()
        self.transactions = TransactionRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера: откат при ошибке и закрытие сессии"""
        if exc_type:
            await self.rollback()
        
        await self.session.close()

    async def commit(self):
        """Фиксация изменений"""
        await self.session.commit()

    async def rollback(self):
        """Откат изменений"""
        await self.session.rollback()
