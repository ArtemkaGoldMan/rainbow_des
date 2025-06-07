# rainbow_des/rainbow/generator_chain.py

from Crypto.Cipher import DES
from .reduction import reduce_hash

def des_hash(password: str) -> bytes:
    """
    Funkcja tworząca 64-bitowy hash z hasła przy użyciu algorytmu DES (ECB).
    Uwaga: używamy stałego klucza i szyfrujemy hasło.
    """
    # Stały klucz 8 bajtów
    key = b'RAINBOW1'
    cipher = DES.new(key, DES.MODE_ECB)

    # Dopełniamy hasło do 8 bajtów
    padded_password = password.ljust(8, '\x00')[:8].encode('utf-8')
    
    # Szyfrujemy hasło
    return cipher.encrypt(padded_password)

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
