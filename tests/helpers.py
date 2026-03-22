import json
from app.crypto.hasher import calculate_hash
from app.crypto.signer import sign_transaction, sign_envelope
from app.crypto.codec import encode_base64
from app.config.settings import settings


from uuid import uuid4

def generate_valid_payload(doc_id: str, timestamp_str: str) -> dict:    
    
    # 3-й уровень вложенности: Документ (Гарантия 201)
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
        "Amount": 1000.50,
        "RevokationInfo": "None",
        "ClaimRightTransfer": "None",
        "PaymentPeriod": "30 days",
        "SignerName": "Ivanov I.I.",
        "AuthorizedPosition": "Director",
        "BankGuaranteeHash": f"HASH-{doc_id}" # Важно для генерации квитка 215
    }
    doc_base64 = encode_base64(json.dumps(doc_content))
    
    # 2-й уровень вложенности: Message
    msg_content = {
        "Data": doc_base64,
        "SenderBranch": "SYSTEM_A",
        "ReceiverBranch": settings.SYSTEM_NAME, # SYSTEM_B
        "InfoMessageType": 201,
        "MessageTime": timestamp_str,
        "ChainGuid": str(uuid4()),
        "PreviousTransactionHash": None,
        "Metadata": None
    }
    msg_base64 = encode_base64(json.dumps(msg_content))
    
    # 1-й уровень вложенности: Transaction
    tx_raw = {
        "TransactionType": 9,
        "Data": msg_base64,
        "SignerCert": encode_base64("SYSTEM_A"),
        "TransactionTime": timestamp_str,
        "Metadata": None,
        "TransactionIn": None,
        "TransactionOut": None
    }
    
    tx_hash = calculate_hash(tx_raw)
    tx_sign = sign_transaction(tx_hash)
    
    tx_raw["Hash"] = tx_hash
    tx_raw["Sign"] = tx_sign
    
    tx_data_dict = {
        "Transactions": [tx_raw],
        "Count": 1
    }
    
    json_tx_data = json.dumps(tx_data_dict)
    base64_payload = encode_base64(json_tx_data)
    
    signed_api_data = {
        "Data": base64_payload,
        "Sign": sign_envelope(base64_payload),
        "SignerCert": encode_base64("SYSTEM_A")
    }
    
    return signed_api_data

def generate_search_payload(start_date: str, end_date: str, limit: int, offset: int) -> dict:
    search_req = {
        "StartDate": start_date,
        "EndDate": end_date,
        "Limit": limit,
        "Offset": offset
    }
    json_search = json.dumps(search_req)
    base64_payload = encode_base64(json_search)
    
    signed_api_data = {
        "Data": base64_payload,
        "Sign": sign_envelope(base64_payload),
        "SignerCert": encode_base64("SYSTEM_A")
    }
    
    return signed_api_data