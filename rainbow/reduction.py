#rainbow_des/rainbow/reduction.py

import string
from typing import List

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
    - pwd_length: docelowa długość hasła (3 znaki)
    - alphabet: dozwolony alfabet znaków (małe litery i cyfry)

    Zwraca:
    - hasło jako ciąg znaków z alfabetu o zadanej długości
    """
    # Konwertuj bajty na liczbę całkowitą
    num = int.from_bytes(hash_bytes, byteorder='big')
    
    # Dodaj round_index do uniknięcia cykli
    num = (num + round_index) & 0xFFFFFFFFFFFFFFFF  # Zachowaj 64 bity
    
    # Konwertuj na ciąg znaków w "bazie" alfabetu
    result: List[str] = []
    for _ in range(pwd_length):
        num, idx = divmod(num, ALPHA_LEN)
        result.append(alphabet[idx])
    
    # Odwróć kolejność
    return ''.join(reversed(result))
