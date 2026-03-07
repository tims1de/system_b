from datetime import datetime
from pydantic import BaseModel


class SearchRequest(BaseModel):
    """Таблица 8. Запрос на получение списка транзакций (outgoing)"""
    StartDate: datetime
    EndDate: datetime
    Limit: int
    Offset: int
