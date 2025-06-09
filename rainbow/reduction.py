"""
Moduł implementujący funkcje redukcji dla tablic tęczowych.
"""

import hashlib
import logging
import logging.handlers
from .config import (
    PASSWORD_ALPHABET,
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
    Redukuje hash DES do hasła o określonej długości przy użyciu SHA-256 jako funkcji mieszającej.
    
    Args:
        hash_bytes: Hash do zredukowania
        step: Numer kroku w łańcuchu
        pwd_length: Długość wyjściowego hasła
        
    Returns:
        Hasło jako string zawierający tylko znaki z PASSWORD_ALPHABET
    """
    if not isinstance(hash_bytes, bytes):
        raise TypeError("Hash musi być bajtami")
        
    if pwd_length < MIN_PASSWORD_LENGTH or pwd_length > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Długość hasła musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
    
    # Mieszanie danych: hash + numer kroku
    data = hash_bytes + step.to_bytes(4, byteorder='big')
    digest = hashlib.sha256(data).digest()

    alphabet_size = len(PASSWORD_ALPHABET)
    password = ''.join(
        PASSWORD_ALPHABET[b % alphabet_size]
        for b in digest[:pwd_length]
    )

    return password
