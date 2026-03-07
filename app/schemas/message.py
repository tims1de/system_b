from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Message(BaseModel):
    """Таблица 3. Информационное сообщение (уровень 2)"""
    Data: str
    SenderBranch: str
    ReceiverBranch: str
    InfoMessageType: int
    MessageTime: datetime
    ChainGuid: UUID
    PreviousTransactionHash: Optional[str] = None
    Metadata: Optional[str] = None
