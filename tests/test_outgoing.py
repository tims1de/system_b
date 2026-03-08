import pytest
import json
from datetime import datetime
from app.schemas.signed_api_data import SignedApiData
from app.crypto.hasher import calculate_hash
from app.crypto.signer import sign_transaction, sign_envelope
from app.crypto.codec import encode_base64, decode_base64
from tests.helpers import generate_valid_payload, generate_search_payload

@pytest.mark.asyncio
async def test_outgoing_messages_success(client):
    """Интеграционный тест: создание транзакции и последующий её поиск через /api/messages/outgoing"""
    # Сначала отправляем транзакцию
    tx_time_str = "2024-03-08T15:00:00"
    payload_in = generate_valid_payload("MSG-OUTGOING-1", tx_time_str)
    
    response_in = await client.post("/api/messages/incoming", json=payload_in)
    assert response_in.status_code == 200
    
    # Делаем запрос на исходящие
    payload_out = generate_search_payload(
        start_date="2024-03-08T14:00:00",
        end_date="2024-03-08T16:00:00",
        limit=10,
        offset=0
    )
    
    response_out = await client.post("/api/messages/outgoing", json=payload_out)
    assert response_out.status_code == 200
    
    resp_body = response_out.json()
    assert "Sign" in resp_body
    assert resp_body["Sign"] != ""
    assert "Data" in resp_body


@pytest.mark.asyncio
async def test_outgoing_messages_invalid_signature(client):
    """Проверка ошибки 400 при отправке поиска с невалидной подписью."""
    payload = generate_search_payload(
        start_date="2024-03-08T14:00:00",
        end_date="2024-03-08T16:00:00",
        limit=10,
        offset=0
    )
    payload["Sign"] = "invalid_sign"
    
    response = await client.post("/api/messages/outgoing", json=payload)
    assert response.status_code == 400
    assert "Invalid envelope signature" in response.json()["detail"]
