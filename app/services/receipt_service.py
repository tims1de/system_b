import json
from datetime import datetime, timezone
from typing import List

from app.schemas.transaction import Transaction
from app.schemas.message import Message
from app.schemas.documents import Receipt215
from app.crypto.codec import encode_base64, decode_base64
from app.crypto.hasher import calculate_hash
from app.crypto.signer import sign_transaction
from app.config.settings import settings

class ReceiptService:
    @staticmethod
    def generate_receipts(incoming_transactions: List[Transaction]) -> List[Transaction]:
        """
        Генерирует квитки (сообщения типа 215) для всех входящих транзакций (кроме самих квитков).
        Возвращает список новых транзакций-квитков для ответа Системе А.
        """
        receipt_transactions = []
        
        for inc_tx in incoming_transactions:
            if inc_tx.TransactionType != 9:
                continue
                
            try:
                # Извлекаем Message
                msg_json_str = decode_base64(inc_tx.Data)
                msg_dict = json.loads(msg_json_str)
                message = Message(**msg_dict)
                
                # Если входящее сообщение само является квитком 215, не генерируем на него квиток
                if message.InfoMessageType == 215:
                    continue
                
                # Получаем BankGuaranteeHash из внутреннего документа
                doc_json_str = decode_base64(message.Data)
                doc_dict = json.loads(doc_json_str)
                bg_hash = doc_dict.get("BankGuaranteeHash")
                if not bg_hash:
                    continue
                
                # Формируем Receipt215 документ
                receipt_doc = Receipt215(BankGuaranteeHash=bg_hash)
                receipt_doc_base64 = encode_base64(receipt_doc.model_dump_json())
                
                # Формируем Message для квитка
                receipt_msg = Message(
                    Data=receipt_doc_base64,
                    SenderBranch=settings.SYSTEM_NAME,  # SYSTEM_B
                    ReceiverBranch=message.SenderBranch, # SYSTEM_A
                    InfoMessageType=215,
                    MessageTime=datetime.now(timezone.utc).isoformat(),
                    ChainGuid=message.ChainGuid,
                    PreviousTransactionHash=inc_tx.Hash,
                    Metadata=None
                )
                receipt_msg_base64 = encode_base64(receipt_msg.model_dump_json())
                
                # Упаковываем в Transaction
                receipt_tx_raw = {
                    "TransactionType": 9,
                    "Data": receipt_msg_base64,
                    "SignerCert": encode_base64(settings.SYSTEM_NAME),
                    "TransactionTime": datetime.now(timezone.utc).isoformat(),
                    "Metadata": None,
                    "TransactionIn": inc_tx.Hash,
                    "TransactionOut": None
                }
                
                # Хэшируем и подписываем квиток
                tx_hash = calculate_hash(receipt_tx_raw)
                tx_sign = sign_transaction(tx_hash)
                
                # Финальный Transaction
                receipt_tx = Transaction(
                    TransactionType=9,
                    Data=receipt_msg_base64,
                    Hash=tx_hash,
                    Sign=tx_sign,
                    SignerCert=encode_base64(settings.SYSTEM_NAME),
                    TransactionTime=receipt_tx_raw["TransactionTime"],
                    Metadata=None,
                    TransactionIn=inc_tx.Hash,
                    TransactionOut=None
                )
                
                receipt_transactions.append(receipt_tx)
                
            except Exception:
                continue
                
        return receipt_transactions
