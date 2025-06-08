# rainbow_des/rainbow/generator_chain.py

"""
Moduł do generowania łańcuchów tęczowych i funkcji redukcji.
"""

import logging
import logging.handlers
import os
import time
from typing import Tuple, Optional
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
from .reduction import reduce_hash
from .config import (
    DES_KEY,
    DES_BLOCK_SIZE,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    Password,
    Hash,
    Chain,
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

def des_hash(password: Password) -> Hash:
    """
    Generuje hash DES dla podanego hasła.
    
    Args:
        password: Hasło do zahashowania
        
    Returns:
        Hash DES jako bajty
        
    Raises:
        ValueError: Jeśli hasło jest nieprawidłowe
        Exception: Dla innych błędów przetwarzania
    """
    try:
        if not isinstance(password, str):
            raise TypeError("Hasło musi być ciągiem znaków")
            
        if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Długość hasła musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
            
        # Przygotowanie danych do szyfrowania
        data = password.encode('utf-8')
        padded_data = pad(data, DES_BLOCK_SIZE)
        
        # Inicjalizacja szyfru DES
        cipher = DES.new(DES_KEY, DES.MODE_ECB)
        
        # Szyfrowanie
        encrypted = cipher.encrypt(padded_data)
        
        # Zwracamy pierwszy blok jako hash
        return encrypted[:DES_BLOCK_SIZE]
        
    except Exception as e:
        logger.exception(f"Błąd podczas generowania hasha DES: {e}")
        raise

def generate_chain(start_password: Password, pwd_length: int, chain_length: int) -> Chain:
    """
    Generuje łańcuch tęczowy zaczynając od podanego hasła.
    
    Args:
        start_password: Hasło startowe
        pwd_length: Długość hasła
        chain_length: Długość łańcucha
        
    Returns:
        Krotka (hasło_startowe, hasło_końcowe)
        
    Raises:
        ValueError: Jeśli parametry są nieprawidłowe
        Exception: Dla innych błędów przetwarzania
    """
    try:
        if not isinstance(start_password, str):
            raise TypeError("Hasło startowe musi być ciągiem znaków")
            
        if len(start_password) != pwd_length:
            raise ValueError(f"Hasło startowe musi mieć długość {pwd_length}")
            
        if chain_length <= 0:
            raise ValueError("Długość łańcucha musi być większa od 0")
            
        current_password = start_password
        
        for i in range(chain_length):
            # Generowanie hasha
            current_hash = des_hash(current_password)
            
            # Redukcja hasha do nowego hasła
            current_password = reduce_hash(current_hash, i, pwd_length)
            
        return start_password, current_password
        
    except Exception as e:
        logger.exception(f"Błąd podczas generowania łańcucha tęczowego: {e}")
        raise