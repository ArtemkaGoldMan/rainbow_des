# rainbow_des/rainbow/crack_hash.py

"""
Moduł do łamania hasł DES przy użyciu tablic tęczowych.
"""

import logging
import logging.handlers
import os
import time
from typing import Optional
from pathlib import Path

from .generator_chain import des_hash, generate_chain
from .reduction import reduce_hash
from .utils import load_table_from_csv, validate_password_length
from .config import (
    DES_BLOCK_SIZE,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_FILE_SIZE,
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

def validate_hash(hash_bytes: Hash) -> None:
    """
    Validates hash format and length.
    
    Args:
        hash_bytes: Hash to validate
        
    Raises:
        TypeError: If hash is not bytes
        ValueError: If hash length is invalid
    """
    if not isinstance(hash_bytes, bytes):
        raise TypeError("Hash must be bytes")
        
    if len(hash_bytes) != DES_BLOCK_SIZE:
        raise ValueError(f"Hash must be exactly {DES_BLOCK_SIZE} bytes ({DES_BLOCK_SIZE * 8} bits)")

def crack_hash(
    target_hash: Hash,
    rainbow_table_file: str,
    pwd_length: int,
    chain_length: int
) -> Optional[Password]:
    """
    Próbuje złamać hash DES używając tablicy tęczowej.
    
    Args:
        target_hash: Hash do złamania
        rainbow_table_file: Ścieżka do pliku z tablicą tęczową
        pwd_length: Długość hasła
        chain_length: Długość łańcucha
        
    Returns:
        Znalezione hasło lub None jeśli nie znaleziono
        
    Raises:
        ValueError: Jeśli parametry są nieprawidłowe
        FileNotFoundError: Jeśli plik tablicy nie istnieje
        Exception: Dla innych błędów przetwarzania
    """
    try:
        # Walidacja parametrów
        if not isinstance(target_hash, bytes):
            raise TypeError("Hash musi być bajtami")
            
        if len(target_hash) != DES_BLOCK_SIZE:
            raise ValueError(f"Hash musi mieć dokładnie {DES_BLOCK_SIZE} bajtów")
            
        if pwd_length < MIN_PASSWORD_LENGTH or pwd_length > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Długość hasła musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
            
        if chain_length <= 0:
            raise ValueError("Długość łańcucha musi być większa od 0")
            
        # Sprawdzenie pliku tablicy
        table_path = Path(rainbow_table_file)
        if not table_path.exists():
            raise FileNotFoundError(f"Nie znaleziono pliku tablicy: {rainbow_table_file}")
            
        # Wczytanie tablicy tęczowej
        print(f"\nWczytywanie tablicy tęczowej z {rainbow_table_file}...")
        logger.info(f"Wczytywanie tablicy tęczowej z {rainbow_table_file}")
        table = dict(load_table_from_csv(rainbow_table_file))  # Convert to dict for faster lookups
        total_chains = len(table)
        print(f"Wczytano {total_chains} łańcuchów")
        
        # Próba znalezienia hasła
        print(f"\nPróba złamania hasha: {target_hash.hex()}")
        logger.info(f"Próba złamania hasha: {target_hash.hex()}")
        
        # Try each possible chain position
        for step in range(chain_length - 1, -1, -1):
            current_hash = target_hash
            
            # Simulate reduction from step to end
            for i in range(step, chain_length):
                pwd_candidate = reduce_hash(current_hash, i, pwd_length)
                current_hash = des_hash(pwd_candidate)
                
            # Check if this end password is in the table
            end_pwd = pwd_candidate
            if end_pwd in table:
                start_pwd = table[end_pwd]
                print(f"Potencjalne dopasowanie łańcucha: {start_pwd} → {end_pwd}")
                
                # Reconstruct chain and verify hash
                test_pwd = start_pwd
                for i in range(chain_length):
                    hashed = des_hash(test_pwd)
                    if hashed == target_hash:
                        print(f"\nZnaleziono hasło: {test_pwd}")
                        logger.info(f"Znaleziono hasło: {test_pwd}")
                        return test_pwd
                    test_pwd = reduce_hash(hashed, i, pwd_length)
                    
        print("\nNie znaleziono hasła")
        logger.info("Nie znaleziono hasła")
        return None
        
    except Exception as e:
        logger.exception(f"Błąd podczas łamania hasha: {e}")
        raise
