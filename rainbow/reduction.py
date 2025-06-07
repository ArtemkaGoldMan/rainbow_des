#rainbow_des/rainbow/reduction.py

import string
import logging
from typing import List

# Konfiguracja logowania
logger = logging.getLogger(__name__)

# Domyślny alfabet: małe litery + cyfry (36 znaków)
DEFAULT_ALPHABET = string.ascii_lowercase + string.digits
ALPHA_LEN = len(DEFAULT_ALPHABET)

def reduce_hash(hash_bytes: bytes, round_index: int, pwd_length: int, alphabet: str = DEFAULT_ALPHABET) -> str:
    """
    Funkcja redukcji odwzorowuje hash na hasło, wykorzystując określony alfabet.
    Zależność od numeru kroku pozwala uniknąć cykli i powtórzeń.

    Argumenty:
    - hash_bytes: wynik funkcji hashującej w postaci bajtów (8 bajtów z DES)
    - round_index: numer kroku w łańcuchu (ważne do unikania cykli)
    - pwd_length: docelowa długość hasła (np. 6 znaków)
    - alphabet: dozwolony alfabet znaków (domyślnie litery + cyfry)

    Zwraca:
    - hasło jako ciąg znaków z alfabetu o zadanej długości
    """
    try:
        if not isinstance(hash_bytes, bytes):
            raise TypeError("Expected hash_bytes to be bytes.")
        if len(hash_bytes) != 8:
            raise ValueError("Expected 8-byte input from DES.")
        if not isinstance(round_index, int) or round_index < 0:
            raise ValueError("round_index must be a non-negative integer.")
        if not isinstance(pwd_length, int) or pwd_length <= 0:
            raise ValueError("pwd_length must be a positive integer.")
        if not isinstance(alphabet, str) or len(alphabet) < 2:
            raise ValueError("alphabet must be a string with at least 2 characters.")

        # Konwertuj bajty na liczbę całkowitą
        num = int.from_bytes(hash_bytes, byteorder='big')

        # Dodaj round_index, zachowaj 64 bity
        num = (num + round_index) & 0xFFFFFFFFFFFFFFFF

        # Konwertuj na hasło w systemie o podstawie ALPHA_LEN
        result: List[str] = []
        for _ in range(pwd_length):
            num, idx = divmod(num, len(alphabet))
            result.append(alphabet[idx])

        password = ''.join(reversed(result))
        logger.debug(f"[reduce_hash] round={round_index}, hash={hash_bytes.hex()} → '{password}'")
        return password

    except Exception as e:
        logger.exception(f"[reduce_hash] Error during reduction: {e}")
        raise
