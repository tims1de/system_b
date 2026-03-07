from pydantic import BaseModel


class SignedApiData(BaseModel):
    """Таблица 1. Конверт запроса/ответа"""
    Data: str
    Sign: str
    SignerCert: str
