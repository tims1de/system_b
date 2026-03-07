from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Transaction(BaseModel):
    """Таблица 2. Транзакция — единица хранения в реестре"""
    TransactionType: int
    Data: str
    Hash: str
    Sign: str
    SignerCert: str
    TransactionTime: datetime
    Metadata: Optional[str] = None
    TransactionIn: Optional[str] = None
    TransactionOut: Optional[str] = None


class TransactionsData(BaseModel):
    """Таблица 9. Ответ со списком транзакций / Тело запроса incoming"""
    Transactions: List[Transaction]
    Count: int
