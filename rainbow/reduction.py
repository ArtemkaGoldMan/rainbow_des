import string

# Domyślny alfabet: małe litery + cyfry (36 znaków)
DEFAULT_ALPHABET = string.ascii_lowercase + string.digits

def reduce_hash(hash_bytes: bytes, round_index: int, pwd_length: int, alphabet: str = DEFAULT_ALPHABET) -> str:
    """
    Funkcja redukująca wynik funkcji skrótu (hash) do postaci hasła o określonej długości.

    Argumenty:
    - hash_bytes: wynik funkcji hashującej w postaci bajtów (np. 8 bajtów z DES)
    - round_index: numer iteracji (ważne do unikania cykli)
    - pwd_length: docelowa długość hasła (np. 6 znaków)
    - alphabet: dozwolony alfabet znaków (np. litery i cyfry)

    Zwraca:
    - hasło jako ciąg znaków z alfabetu o zadanej długości
    """

    # Długość alfabetu (np. 36 dla a-z0-9)
    alpha_len = len(alphabet)

    # Konwersja bajtów hash na liczbę całkowitą
    num = int.from_bytes(hash_bytes, byteorder='big')

    # Dodajemy round_index, aby każdy etap dawał inne wyniki
    num = (num + round_index) % (alpha_len ** pwd_length)

    # Zamieniamy liczbę na ciąg znaków w "bazie" alfabetu
    result = []
    for _ in range(pwd_length):
        num, idx = divmod(num, alpha_len)
        result.append(alphabet[idx])

    # Odwracamy kolejność, aby mieć poprawne hasło
    return ''.join(reversed(result))
