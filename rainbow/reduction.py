#rainbow_des/rainbow/reduction.py

"""
Moduł implementujący funkcje redukcji dla tablic tęczowych.
"""

import logging
import logging.handlers
import os
import time
from typing import Optional
from .config import (
    PASSWORD_ALPHABET,
    DES_BLOCK_SIZE,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    Password,
    Hash,
    LOG_FORMAT,
    LOG_LEVEL,
    LOG_FILE,
    MAX_LOG_SIZE,
    MAX_LOG_FILES
)

# Konfiguracja logowania z rotacją
handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=MAX_LOG_SIZE,
    backupCount=MAX_LOG_FILES
)
handler.setFormatter(logging.Formatter(LOG_FORMAT))

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(handler)

def reduce_hash(hash_bytes: Hash, step: int, pwd_length: int) -> Password:
    """
    Redukuje hash do hasła o określonej długości.
    Używa kroku jako dodatkowego parametru dla różnorodności.
    
    Args:
        hash_bytes: Hash do zredukowania
        step: Numer kroku w łańcuchu
        pwd_length: Oczekiwana długość hasła
        
    Returns:
        Wygenerowane hasło
        
    Raises:
        ValueError: Jeśli parametry są nieprawidłowe
        Exception: Dla innych błędów przetwarzania
    """
    try:
        if not isinstance(hash_bytes, bytes):
            raise TypeError("Hash musi być bajtami")
            
        if not isinstance(step, int) or step < 0:
            raise ValueError("Krok musi być nieujemną liczbą całkowitą")
            
        if pwd_length < MIN_PASSWORD_LENGTH or pwd_length > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Długość hasła musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
            
        # Konwersja hasha na liczbę
        hash_int = int.from_bytes(hash_bytes, byteorder='big')
        
        # Dodanie kroku dla różnorodności
        hash_int = (hash_int + step) % (1 << 64)
        
        # Generowanie hasła
        result = []
        for _ in range(pwd_length):
            hash_int, remainder = divmod(hash_int, len(PASSWORD_ALPHABET))
            result.append(PASSWORD_ALPHABET[remainder])
            
        return ''.join(result)
        
    except Exception as e:
        logger.exception(f"Błąd podczas redukcji hasha: {e}")
        raise
