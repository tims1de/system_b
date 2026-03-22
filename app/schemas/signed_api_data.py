from pydantic import BaseModel


class SignedApiData(BaseModel):
    """Конверт запроса/ответа"""
    Data: str
    Sign: str
    SignerCert: str
