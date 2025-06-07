from typing import Optional, Tuple
from .generator_chain import des_hash
from .reduction import reduce_hash
from .utils import load_table_from_csv, validate_password_length

def crack_hash(target_hash: bytes, rainbow_table_file: str, pwd_length: int, chain_length: int) -> Optional[str]:
    """
    Próbuje złamać hash używając tablicy tęczowej.
    
    Argumenty:
    - target_hash: hash do złamania (8 bajtów)
    - rainbow_table_file: ścieżka do pliku z tablicą tęczową
    - pwd_length: długość hasła
    - chain_length: długość łańcucha użyta do generowania tablicy
    
    Zwraca:
    - znalezione hasło lub None jeśli nie znaleziono
    """
    # Wczytaj tablicę tęczową
    rainbow_table = dict(load_table_from_csv(rainbow_table_file))
    
    # Dla każdego kroku w łańcuchu
    for step in range(chain_length):
        # Wygeneruj potencjalne końcowe hasło
        current_hash = target_hash
        current_pwd = None
        
        # Przejdź przez pozostałe kroki łańcucha
        for i in range(step, chain_length):
            current_pwd = reduce_hash(current_hash, i, pwd_length)
            current_hash = des_hash(current_pwd)
        
        # Sprawdź czy znalezione końcowe hasło jest w tablicy
        if current_pwd in rainbow_table:
            # Znaleziono dopasowanie - odtwórz łańcuch od początku
            start_pwd = rainbow_table[current_pwd]
            test_pwd = start_pwd
            
            # Przejdź przez łańcuch do kroku, w którym znaleziono hash
            for i in range(chain_length):
                if des_hash(test_pwd) == target_hash:
                    return test_pwd
                test_pwd = reduce_hash(des_hash(test_pwd), i, pwd_length)
    
    return None 