from modules.user.utils import generate_api_key, verify_api_key


def test_generate_api_key_returns_tuple_of_two_strings():
    raw_key, encrypted = generate_api_key()
    assert isinstance(raw_key, str)
    assert isinstance(encrypted, str)


def test_generate_api_key_raw_starts_with_fin_prefix():
    raw_key, _ = generate_api_key()
    assert raw_key.startswith("fin_")


def test_generate_api_key_encrypted_is_sha256_hex():
    _, encrypted = generate_api_key()
    assert len(encrypted) == 64
    assert all(c in "0123456789abcdef" for c in encrypted)


def test_generate_api_key_produces_different_keys():
    key1, _ = generate_api_key()
    key2, _ = generate_api_key()
    assert key1 != key2


def test_verify_api_key_returns_true_for_valid_pair():
    raw_key, encrypted = generate_api_key()
    assert verify_api_key(raw_key, encrypted) is True


def test_verify_api_key_returns_false_for_invalid_raw_key():
    _, encrypted = generate_api_key()
    assert verify_api_key("fin_wrong_key", encrypted) is False


def test_verify_api_key_returns_false_for_tampered_raw_key():
    raw_key, encrypted = generate_api_key()
    tampered = raw_key[:-1] + ("x" if raw_key[-1] != "x" else "y")
    assert verify_api_key(tampered, encrypted) is False


def test_verify_api_key_returns_false_for_invalid_encrypted_key():
    raw_key, _ = generate_api_key()
    assert verify_api_key(raw_key, "invalid_hex") is False


def test_verify_api_key_returns_false_for_empty_raw_key():
    _, encrypted = generate_api_key()
    assert verify_api_key("", encrypted) is False
