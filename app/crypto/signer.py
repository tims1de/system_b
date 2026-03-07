from app.crypto.codec import bytes_to_base64
from app.crypto.hasher import calculate_data_hash


def sign_transaction(hash_str: str) -> str:
    """
    Алгоритм 4.2: Эмуляция ЭЦП транзакции.
    Base64(UTF8(Hash_Hex_String))
    """
    return bytes_to_base64(hash_str.encode("utf-8"))


def sign_envelope(base64_data: str) -> str:
    """
    Алгоритм 5.1: Эмуляция ЭЦП конверта SignedApiData.
    Base64(SHA256(Base64_Data))
    """
    digest = calculate_data_hash(base64_data)
    return bytes_to_base64(digest)


def verify_transaction_sign(hash_str: str, sign: str) -> bool:
    """Проверка эмулированной подписи транзакции"""
    return sign == sign_transaction(hash_str)


def verify_envelope_sign(base64_data: str, sign: str) -> bool:
    """Проверка подписи конверта"""
    return sign == sign_envelope(base64_data)
