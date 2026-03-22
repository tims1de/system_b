from datetime import datetime
from typing import List
from pydantic import BaseModel


class Taxs(BaseModel):
    """Сведения о налогах"""
    Number: str
    NameTax: str
    Amount: float
    PennyAmount: float


class Obligation(BaseModel):
    """Сведения об обязательстве"""
    Type: int
    StartDate: datetime
    EndDate: datetime
    ActDate: datetime
    ActNumber: str
    Taxs: List[Taxs]


class Guarantee201(BaseModel):
    """Сообщение о выдаче гарантии (201)"""
    InformationType: int = 201
    InformationTypeString: str = "Выдача гарантии"
    Number: str
    IssuedDate: datetime
    Guarantor: str
    Beneficiary: str
    Principal: str
    Obligations: List[Obligation]
    StartDate: datetime
    EndDate: datetime
    CurrencyCode: str
    CurrencyName: str
    Amount: float
    RevokationInfo: str
    ClaimRightTransfer: str
    PaymentPeriod: str
    SignerName: str
    AuthorizedPosition: str
    BankGuaranteeHash: str


class Acceptance202(BaseModel):
    """Сообщение о принятии гарантии (202)"""
    Name: str
    BankGuaranteeHash: str
    Sign: str
    SignerCert: str


class Rejection203(BaseModel):
    """Сообщение об отказе в принятии гарантии (203)"""
    Name: str
    BankGuaranteeHash: str
    Sign: str
    SignerCert: str
    Reason: str


class Receipt215(BaseModel):
    """Квиток (215)"""
    BankGuaranteeHash: str
