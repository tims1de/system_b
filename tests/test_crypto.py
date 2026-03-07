import pytest
import json
from app.crypto.hasher import calculate_hash, calculate_data_hash
from app.crypto.signer import sign_transaction, verify_transaction_sign, sign_envelope, verify_envelope_sign
from app.crypto.codec import encode_base64, decode_base64


def test_base64_codec():
    original = "Hello, World!"
    encoded = encode_base64(original)
    decoded = decode_base64(encoded)
    assert decoded == original


def test_transaction_hash_and_sign():
    tx_data = {
        "TransactionType": 9,
        "Data": "base64data",
        "Hash": "REPLACE_ME",
        "Sign": "REPLACE_ME",
        "SignerCert": "cert",
        "TransactionTime": "2024-01-01T00:00:00Z"
    }
    
    # 1. Вычисляем хэш
    tx_hash = calculate_hash(tx_data)
    assert len(tx_hash) == 64  # SHA-256 hex length
    
    # 2. Подписываем (эмуляция)
    tx_sign = sign_transaction(tx_hash)
    
    # 3. Проверяем подпись
    assert verify_transaction_sign(tx_hash, tx_sign) is True
    assert verify_transaction_sign(tx_hash, "wrong_sign") is False


def test_envelope_sign():
    base64_data = encode_base64(json.dumps({"test": "data"}))
    envelope_sign = sign_envelope(base64_data)
    
    assert verify_envelope_sign(base64_data, envelope_sign) is True
    assert verify_envelope_sign(base64_data, "wrong_sign") is False


def test_hash_determinism():
    data = {"b": 2, "a": 1, "Hash": "old", "Sign": "old"}
    hash1 = calculate_hash(data)
    
    data_reordered = {"a": 1, "Hash": "new", "b": 2, "Sign": "new"}
    hash2 = calculate_hash(data_reordered)
    
    # Хэш должен быть одинаковым независимо от порядка ключей во входном дикте
    # т.к. json.dumps(sort_keys=True) используется внутри
    assert hash1 == hash2
