import hashlib
import secrets


def generate_api_key() -> tuple[str, str]:
    raw_key = f"fin_{secrets.token_urlsafe(32)}"
    encrypted = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, encrypted


def verify_api_key(raw_key: str, encrypted_key: str) -> bool:
    return hashlib.sha256(raw_key.encode()).hexdigest() == encrypted_key
