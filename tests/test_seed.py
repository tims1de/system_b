import pytest
import json
from app.storage.unit_of_work import UnitOfWork
from app.services.seed_service import seed_test_data
from app.crypto.codec import decode_base64

@pytest
async def test_seed_test_data_generates_transactions(uow: UnitOfWork):
    """Тест проверяет, что при пустой базе функция seed_test_data создает 2 транзакции."""
    await seed_test_data(uow)
    
    transactions = await uow.transactions.list_all()
            
    assert len(transactions) >= 2, "Seed data was not generated correctly"
            
    found_201 = False
    found_202 = False
            
    for tx in transactions:
        if tx.transaction_type == 9:
            msg_dict = json.loads(decode_base64(tx.data))
            if msg_dict.get("InfoMessageType") == 201:
                found_201 = True
            elif msg_dict.get("InfoMessageType") == 202:
                found_202 = True
                        
    assert found_201, "Transaction 201 was not seeded"
    assert found_202, "Transaction 202 was not seeded"


@pytest
async def test_seed_test_data_idempotency(uow: UnitOfWork):
    """Тест проверяет, что повторный вызов seed_test_data не создает дубликаты."""
    await seed_test_data(uow)
    
    initial_count = len(await uow.transactions.list_all())
            
    await seed_test_data(uow)
    
    final_count = len(await uow.transactions.list_all())

    assert initial_count == final_count, "Seed data is not idempotent"
