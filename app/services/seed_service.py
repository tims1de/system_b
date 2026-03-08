import json
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import Depends
from app.storage.unit_of_work import UnitOfWork
from app.crypto.hasher import calculate_hash
from app.crypto.signer import sign_transaction
from app.crypto.codec import encode_base64
from app.config.settings import settings
from app.storage.models import TransactionModel

async def seed_test_data(uow: UnitOfWork = Depends(UnitOfWork)) -> None:
    """Генерация стартовых тестовых данных, если БД пуста."""
    async with uow:
        existing = await uow.transactions.list_all()
        if len(existing) > 0:
            return

        print("Seeding initial test data...")
        now = datetime.now(timezone.utc)
        timestamp_str = now.isoformat()

        tx_201_raw, tx_hash_201, tx_sign_201 = _generate_transaction_data(
            doc_id="SEED-MSG-201",
            info_type=201,
            timestamp_str=timestamp_str
        )
        
        model_201 = TransactionModel(
            transaction_type=tx_201_raw["TransactionType"],
            data=tx_201_raw["Data"],
            hash=tx_hash_201,
            sign=tx_sign_201,
            signer_cert=tx_201_raw["SignerCert"],
            transaction_time=now,
            metadata_info=tx_201_raw["Metadata"],
            transaction_in=tx_201_raw["TransactionIn"],
            transaction_out=tx_201_raw["TransactionOut"]
        )
        await uow.transactions.add(model_201)
        
        # Создадим одну транзакцию "Принятие гарантии" (202)
        tx_202_raw, tx_hash_202, tx_sign_202 = _generate_transaction_data(
            doc_id="SEED-MSG-202",
            info_type=202,
            timestamp_str=timestamp_str
        )
        
        model_202 = TransactionModel(
            transaction_type=tx_202_raw["TransactionType"],
            data=tx_202_raw["Data"],
            hash=tx_hash_202,
            sign=tx_sign_202,
            signer_cert=tx_202_raw["SignerCert"],
            transaction_time=now,
            metadata_info=tx_202_raw["Metadata"],
            transaction_in=tx_202_raw["TransactionIn"],
            transaction_out=tx_202_raw["TransactionOut"]
        )
        await uow.transactions.add(model_202)

        await uow.commit()
        print("Successfully seeded initial test data.")

def _generate_transaction_data(doc_id: str, info_type: int, timestamp_str: str):
    # 3-й уровень
    if info_type == 201:
        doc_content = {
            "InformationType": 201,
            "InformationTypeString": "Выдача гарантии",
            "Number": doc_id,
            "IssuedDate": timestamp_str,
            "Guarantor": "Test Guarantor",
            "Beneficiary": "Test Beneficiary",
            "Principal": "Test Principal",
            "Obligations": [],
            "StartDate": timestamp_str,
            "EndDate": timestamp_str,
            "CurrencyCode": "RUB",
            "CurrencyName": "Российский рубль",
            "Amount": 10000.0,
            "RevokationInfo": "None",
            "ClaimRightTransfer": "None",
            "PaymentPeriod": "30 days",
            "SignerName": "Ivanov I.I.",
            "AuthorizedPosition": "Director",
            "BankGuaranteeHash": f"HASH-{doc_id}"
        }
    else:
        doc_content = {
            "Name": "Acceptance",
            "BankGuaranteeHash": f"HASH-{doc_id}-ACCEPTED",
            "Sign": "SomeSign",
            "SignerCert": "Cert"
        }
        
    doc_base64 = encode_base64(json.dumps(doc_content))
    
    # 2-й уровень - Message
    msg_content = {
        "Data": doc_base64,
        "SenderBranch": settings.SYSTEM_NAME,
        "ReceiverBranch": "SYSTEM_A",
        "InfoMessageType": info_type,
        "MessageTime": timestamp_str,
        "ChainGuid": str(uuid4()),
        "PreviousTransactionHash": None,
        "Metadata": None
    }
    msg_base64 = encode_base64(json.dumps(msg_content))
    
    # 1-й уровень - Transaction
    tx_raw = {
        "TransactionType": 9,
        "Data": msg_base64,
        "SignerCert": encode_base64(settings.SYSTEM_NAME),
        "TransactionTime": timestamp_str,
        "Metadata": None,
        "TransactionIn": None,
        "TransactionOut": None
    }
    
    tx_hash = calculate_hash(tx_raw)
    tx_sign = sign_transaction(tx_hash)
    
    return tx_raw, tx_hash, tx_sign
