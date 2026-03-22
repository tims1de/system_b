from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Transaction(BaseModel):
    """Транзакция"""
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
    """Ответ со списком транзакций / Тело запроса incoming"""
    Transactions: List[Transaction]
    Count: int
