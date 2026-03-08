import json
from typing import List

from app.schemas.signed_api_data import SignedApiData
from app.schemas.transaction import Transaction, TransactionsData
from app.crypto.signer import verify_envelope_sign, verify_transaction_sign, sign_envelope
from app.crypto.hasher import calculate_hash
from app.crypto.codec import decode_base64, encode_base64
from app.storage.unit_of_work import UnitOfWork
from app.storage.models import TransactionModel
from app.config.settings import settings


class MessageService:
    """Сервис для обработки входящих и исходящих сообщений"""

    @staticmethod
    async def process_incoming(signed_data: SignedApiData, uow: UnitOfWork) -> SignedApiData:
        """
        Алгоритм 3.1: Обработка входящих сообщений.
        1. Проверка подписи конверта.
        2. Декодирование данных в TransactionsData.
        3. Валидация каждой транзакции (хэш и подпись).
        4. Сохранение транзакций в БД.
        """
        # Проверка подписи конверта
        if not verify_envelope_sign(signed_data.Data, signed_data.Sign):
            raise ValueError("Invalid envelope signature")

        # Декодирование данных
        try:
            json_str = decode_base64(signed_data.Data)
            data_dict = json.loads(json_str)
            # Валидируем общую структуру через Pydantic
            transactions_data = TransactionsData(**data_dict)
        except Exception as e:
            raise ValueError(f"Invalid data format: {e}")

        processed_transactions: List[Transaction] = []
        
        # Получаем сырой список транзакций для корректного расчета хэша
        transactions_raw = data_dict.get("Transactions", [])

        async with uow:
            for i, tx_schema in enumerate(transactions_data.Transactions):
                # Достаем сырой словарь для этой транзакции для проверки хэша
                tx_raw = transactions_raw[i]
                calculated_hash = calculate_hash(tx_raw)
                
                if calculated_hash != tx_schema.Hash:
                    raise ValueError(f"Invalid transaction hash for {tx_schema.Hash}. Server calculated: {calculated_hash}")
                
                if not verify_transaction_sign(tx_schema.Hash, tx_schema.Sign):
                    raise ValueError(f"Invalid transaction signature for {tx_schema.Hash}")

                # Сохраняем в БД используя провалидированные данные
                tx_model = TransactionModel(
                    transaction_type=tx_schema.TransactionType,
                    data=tx_schema.Data,
                    hash=tx_schema.Hash,
                    sign=tx_schema.Sign,
                    signer_cert=tx_schema.SignerCert,
                    transaction_time=tx_schema.TransactionTime,
                    metadata_info=tx_schema.Metadata,
                    transaction_in=tx_schema.TransactionIn,
                    transaction_out=tx_schema.TransactionOut
                )
                await uow.transactions.add(tx_model)
                processed_transactions.append(tx_schema)

            try:
                await uow.commit()
            except Exception as e:
                if "UNIQUE constraint failed" in str(e) or "UniqueViolation" in str(e):
                    raise ValueError("One or more transactions already exist (duplicate hash).")
                raise e

        response_payload = TransactionsData(
            Transactions=processed_transactions,
            Count=len(processed_transactions)
        )
        json_response = response_payload.model_dump_json()
        base64_response = encode_base64(json_response)
        
        return SignedApiData(
            Data=base64_response,
            Sign=sign_envelope(base64_response),
            SignerCert=encode_base64(settings.SYSTEM_NAME)
        )
