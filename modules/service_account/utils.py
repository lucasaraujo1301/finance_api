import hashlib
import secrets


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def generate_api_key() -> tuple[str, str]:
    raw_key = f"fin_{secrets.token_urlsafe(32)}"
    encrypted = hash_api_key(raw_key)
    return raw_key, encrypted


def verify_api_key(raw_key: str, encrypted_key: str) -> bool:
    return hash_api_key(raw_key) == encrypted_key
