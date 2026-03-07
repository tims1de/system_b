import base64


def encode_base64(data: str) -> str:
    """Кодирует строку UTF-8 в Base64"""
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def decode_base64(data: str) -> str:
    """Декодирует Base64 в строку UTF-8"""
    return base64.b64decode(data).decode("utf-8")


def bytes_to_base64(data: bytes) -> str:
    """Кодирует байты в Base64"""
    return base64.b64encode(data).decode("utf-8")


def base64_to_bytes(data: str) -> bytes:
    """Декодирует Base64 в байты"""
    return base64.b64decode(data)
