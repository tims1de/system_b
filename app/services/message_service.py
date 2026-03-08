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
from app.schemas.search import SearchRequest


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

    @staticmethod
    async def process_outgoing(signed_data: SignedApiData, uow: UnitOfWork) -> SignedApiData:
        """
        Алгоритм 3.2: Выдача исходящих сообщений.
        1. Проверка подписи конверта.
        2. Декодирование SearchRequest (StartDate, EndDate, Limit, Offset).
        3. Фильтрация и пагинация транзакций из БД.
        4. Упаковка ответа в TransactionsData -> SignedApiData.
        """
        # Проверка подписи конверта
        if not verify_envelope_sign(signed_data.Data, signed_data.Sign):
            raise ValueError("Invalid envelope signature")
            
        # Декодирование SearchRequest
        try:
            json_str = decode_base64(signed_data.Data)
            data_dict = json.loads(json_str)
            search_request = SearchRequest(**data_dict)
        except Exception as e:
            raise ValueError(f"Invalid search request data format: {e}")

        # Получение транзакций из БД
        async with uow:
            db_transactions = await uow.transactions.get_filtered(
                start_date=search_request.StartDate,
                end_date=search_request.EndDate,
                limit=1000,
                offset=0
            )

        processed_transactions: List[Transaction] = []
        
        for tx_model in db_transactions:
            tx_schema = Transaction(
                TransactionType=tx_model.transaction_type,
                Data=tx_model.data,
                Hash=tx_model.hash,
                Sign=tx_model.sign,
                SignerCert=tx_model.signer_cert,
                TransactionTime=tx_model.transaction_time.isoformat(),
                Metadata=tx_model.metadata_info,
                TransactionIn=tx_model.transaction_in,
                TransactionOut=tx_model.transaction_out
            )
            
            # Фильтрация по ReceiverBranch = "SYSTEM_A" для информационных сообщений (Type=9)
            if tx_schema.TransactionType == 9:
                try:
                    msg_json_str = decode_base64(tx_schema.Data)
                    msg_dict = json.loads(msg_json_str)
                    if msg_dict.get("ReceiverBranch") != "SYSTEM_A":
                        continue
                except:
                    pass
            
            processed_transactions.append(tx_schema)
            
        # Применение пагинации (Limit, Offset)
        paginated_transactions = processed_transactions[search_request.Offset : search_request.Offset + search_request.Limit]

        response_payload = TransactionsData(
            Transactions=paginated_transactions,
            Count=len(paginated_transactions)
        )
        json_response = response_payload.model_dump_json()
        base64_response = encode_base64(json_response)
        
        return SignedApiData(
            Data=base64_response,
            Sign=sign_envelope(base64_response),
            SignerCert=encode_base64(settings.SYSTEM_NAME)
        )

