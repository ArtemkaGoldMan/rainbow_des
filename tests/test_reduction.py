from rainbow.reduction import reduce_hash

def test_reduce_hash_basic():
    # Przykładowy hash w postaci 8 bajtów (symulacja DES)
    hash_bytes = b'\x01\x02\x03\x04\x05\x06\x07\x08'

    # Dwa wywołania z różnymi round_index — powinny dać różne hasła
    result1 = reduce_hash(hash_bytes, round_index=0, pwd_length=6)
    result2 = reduce_hash(hash_bytes, round_index=1, pwd_length=6)

    # Sprawdzenie, czy wynik jest poprawny
    assert isinstance(result1, str)
    assert len(result1) == 6
    assert result1 != result2  # round_index powinien wpływać na wynik
