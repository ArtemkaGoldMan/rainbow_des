# rainbow_des/rainbow/generator_chain.py

from Crypto.Cipher import DES
from .reduction import reduce_hash

def des_hash(password: str) -> bytes:
    """
    Funkcja tworząca 64-bitowy hash z hasła przy użyciu algorytmu DES (ECB).
    Uwaga: używamy hasła jako klucza i szyfrujemy pusty blok.
    To uproszczona forma funkcji haszującej.
    """
    # Hasło musi mieć dokładnie 8 bajtów – dopełniamy zerami jeśli trzeba
    key = password.ljust(8, '\x00')[:8].encode('utf-8')
    cipher = DES.new(key, DES.MODE_ECB)

    # Szyfrujemy pusty blok (8 bajtów zer) – wynik traktujemy jako hash
    return cipher.encrypt(b'\x00' * 8)

def generate_chain(start_pwd: str, pwd_length: int, chain_length: int) -> tuple[str, str]:
    """
    Generuje jeden łańcuch tęczowy:
    start_pwd → hash → reduce → hash → ... → end_pwd

    Argumenty:
    - start_pwd: hasło początkowe
    - pwd_length: długość hasła (np. 6)
    - chain_length: liczba iteracji (np. 1000)

    Zwraca:
    - krotkę (start_pwd, end_pwd)
    """
    pwd = start_pwd

    for i in range(chain_length):
        h = des_hash(pwd)
        pwd = reduce_hash(h, i, pwd_length)

    return start_pwd, pwd
