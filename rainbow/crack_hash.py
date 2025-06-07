# rainbow_des/rainbow/crack_hash.py

import logging
from typing import Optional
from .generator_chain import des_hash
from .reduction import reduce_hash
from .utils import load_table_from_csv

logger = logging.getLogger(__name__)

def crack_hash(target_hash: bytes, rainbow_table_file: str, pwd_length: int, chain_length: int) -> Optional[str]:
    """
    Próbuje złamać hash używając tablicy tęczowej.
    Zwraca: znalezione hasło lub None jeśli nie znaleziono.
    """
    if len(target_hash) != 8:
        logger.error("Błąd: hash musi mieć dokładnie 8 bajtów (64 bity)")
        return None

    try:
        table_entries = load_table_from_csv(rainbow_table_file)
    except FileNotFoundError:
        logger.error(f"Nie znaleziono pliku tablicy: {rainbow_table_file}")
        return None
    except Exception as e:
        logger.exception(f"Błąd podczas wczytywania tablicy: {e}")
        return None

    rainbow_table = dict(table_entries)

    logger.info(f"🔍 Rozpoczynam próbę złamania: {target_hash.hex()}")

    # Przechodzimy od końca łańcucha do początku
    for step in range(chain_length - 1, -1, -1):
        current_hash = target_hash

        # Symulujemy redukcję od kroku `step` do końca
        for i in range(step, chain_length):
            pwd_candidate = reduce_hash(current_hash, i, pwd_length)
            current_hash = des_hash(pwd_candidate)

        # Czy to końcówka znaleziona w tablicy?
        end_pwd = pwd_candidate
        if end_pwd in rainbow_table:
            start_pwd = rainbow_table[end_pwd]
            logger.info(f"Potencjalne dopasowanie łańcucha: {start_pwd} → {end_pwd}")

            # Odtworzenie łańcucha i porównanie hashy
            test_pwd = start_pwd
            for i in range(chain_length):
                hashed = des_hash(test_pwd)
                if hashed == target_hash:
                    logger.info(f"Sukces! Oryginalne hasło: {test_pwd}")
                    return test_pwd
                test_pwd = reduce_hash(hashed, i, pwd_length)

    logger.warning("Nie znaleziono hasła w tablicy.")
    return None
