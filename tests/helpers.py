import json
from app.crypto.hasher import calculate_hash
from app.crypto.signer import sign_transaction, sign_envelope
from app.crypto.codec import encode_base64


def generate_valid_payload(doc_id: str, timestamp_str: str) -> dict:
    doc_content = {"DocumentID": doc_id, "Content": "Test Content"}
    doc_base64 = encode_base64(json.dumps(doc_content))
    
    tx_raw = {
        "TransactionType": 201,
        "Data": doc_base64,
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
