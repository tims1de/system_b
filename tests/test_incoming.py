import pytest
import json
from app.crypto.hasher import calculate_hash
from app.crypto.signer import sign_transaction, sign_envelope
from app.crypto.codec import encode_base64, decode_base64
from tests.helpers import generate_valid_payload

@pytest.mark.asyncio
async def test_incoming_messages_full_cycle(client):
    """Интеграционный тест: успешная отправка валидного сообщения."""
    payload = generate_valid_payload("MSG-001", "2024-03-08T10:00:00")
    
    response = await client.post("/api/messages/incoming", json=payload)
    assert response.status_code == 200
    
    resp_body = response.json()
    assert "Sign" in resp_body
    assert resp_body["Sign"] != ""
    
    # Проверка на наличие сгенерированного квитка
    out_data = json.loads(decode_base64(resp_body["Data"]))
    assert out_data["Count"] == 2
    assert len(out_data["Transactions"]) == 2
    
    # Вторая транзакция должна быть квитком от SYSTEM_B
    receipt_tx = out_data["Transactions"][1]
    receipt_msg = json.loads(decode_base64(receipt_tx["Data"]))
    assert receipt_msg["InfoMessageType"] == 215
    assert receipt_msg["SenderBranch"] == "SYSTEM_B"



@pytest.mark.asyncio
async def test_incoming_invalid_envelope_signature(client):
    """Проверка ошибки 400 при отправке данных с невалидной подписью конверта."""
    payload = generate_valid_payload("MSG-ERROR", "2024-03-08T10:05:00")
    payload["Sign"] = "invalid_sign"
    
    response = await client.post("/api/messages/incoming", json=payload)
    assert response.status_code == 400
    assert "Invalid envelope signature" in response.json()["detail"]


@pytest.mark.asyncio
async def test_incoming_messages_duplicate_hash(client):
    """Проверка ошибки 400 при попытке сохранить дубликат транзакции."""
    payload = generate_valid_payload("MSG-DUP", "2024-03-08T10:10:00")
    
    # Первая отправка - успешно
    response1 = await client.post("/api/messages/incoming", json=payload)
    assert response1.status_code == 200
    
    # Вторая отправка того же пакета - ошибка уникальности хэша
    response2 = await client.post("/api/messages/incoming", json=payload)
    assert response2.status_code == 400
    assert "One or more transactions already exist" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_incoming_messages_different_inputs(client):
    """Проверка обработки пакета с несколькими транзакциями разного типа."""
    doc1 = {"DocumentID": "DOC-MULTI-1", "Content": "First"}
    doc2 = {"DocumentID": "DOC-MULTI-2", "Content": "Second"}
    
    tx1 = {
        "TransactionType": 201,
        "Data": encode_base64(json.dumps(doc1)),
        "SignerCert": encode_base64("SYSTEM_A"),
        "TransactionTime": "2024-03-08T10:15:00",
        "Metadata": None,
        "TransactionIn": None,
        "TransactionOut": None
    }
    tx1["Hash"] = calculate_hash(tx1)
    tx1["Sign"] = sign_transaction(tx1["Hash"])
    
    tx2 = {
        "TransactionType": 202,
        "Data": encode_base64(json.dumps(doc2)),
        "SignerCert": encode_base64("SYSTEM_B"),
        "TransactionTime": "2024-03-08T10:16:00",
        "Metadata": encode_base64(json.dumps({"info": "meta"})),
        "TransactionIn": tx1["Hash"],
        "TransactionOut": None
    }
    tx2["Hash"] = calculate_hash(tx2)
    tx2["Sign"] = sign_transaction(tx2["Hash"])
    
    tx_data_dict = {
        "Transactions": [tx1, tx2],
        "Count": 2
    }
    
    base64_payload = encode_base64(json.dumps(tx_data_dict))
    
    payload = {
        "Data": base64_payload,
        "Sign": sign_envelope(base64_payload),
        "SignerCert": encode_base64("SYSTEM_A")
    }
    
    response = await client.post("/api/messages/incoming", json=payload)
    assert response.status_code == 200
    
    resp_body = response.json()
    assert "Sign" in resp_body
