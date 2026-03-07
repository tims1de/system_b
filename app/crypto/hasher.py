import hashlib
import json
from typing import Any, Dict


def calculate_hash(data: Dict[str, Any]) -> str:
    """
    Алгоритм 4.1: Вычисление хэша транзакции.
    1. Клонируем данные.
    2. Устанавливаем Hash и Sign в "".
    3. Сериализуем в JSON (без пробелов, сортировка ключей для детерминизма).
    4. SHA256 -> HEX UPPERCASE.
    """
    payload = data.copy()
    payload["Hash"] = ""
    payload["Sign"] = ""

    # Сериализация: компактный вид, сортировка полей для стабильности хэша
    json_str = json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    
    hash_object = hashlib.sha256(json_str.encode("utf-8"))
    return hash_object.hexdigest().upper()


def calculate_data_hash(base64_data: str) -> bytes:
    """
    Алгоритм 5.1: Часть вычисления SignedApiData.Sign.
    SHA256(Base64_String) -> bytes
    """
    return hashlib.sha256(base64_data.encode("utf-8")).digest()
