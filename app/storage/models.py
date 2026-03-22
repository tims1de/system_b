from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для моделей SQLAlchemy"""
    pass


class TransactionModel(Base):
    """
    Модель транзакции
    """
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    transaction_type: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[str] = mapped_column(String, nullable=False)
    hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    sign: Mapped[str] = mapped_column(String, nullable=False)
    signer_cert: Mapped[str] = mapped_column(String, nullable=False)
    transaction_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    metadata_info: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    transaction_in: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    transaction_out: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<Transaction(hash={self.hash[:8]}..., type={self.transaction_type})>"
