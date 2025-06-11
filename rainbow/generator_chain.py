# rainbow_des/rainbow/generator_chain.py

"""
Moduł do generowania łańcuchów tęczowych i funkcji redukcji.
"""

import logging
import logging.handlers
from typing import Tuple, List
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import os
import time
from multiprocessing import Pool

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

        data_bytes = password.encode('utf-8')
        padded_data = pad(data_bytes, DES_BLOCK_SIZE)
        cipher = DES.new(DES_KEY, DES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(padded_data)

        return encrypted_bytes[:DES_BLOCK_SIZE]

    except Exception as error:
        logger.exception(f"Błąd podczas generowania hasha DES: {error}")
        raise


def generate_chain(start_password: Password, password_length: int, chain_length: int) -> Chain:
    """
    Generuje łańcuch tęczowy zaczynając od podanego hasła.

    Args:
        start_password: Hasło startowe
        password_length: Długość hasła
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

        if len(start_password) != password_length:
            raise ValueError(f"Hasło startowe musi mieć długość {password_length}")

        if chain_length <= 0:
            raise ValueError("Długość łańcucha musi być większa od 0")

        current_password = start_password
        seen_passwords = {current_password}

        for step_index in range(chain_length):
            hashed_bytes = des_hash(current_password)
            reduced_password = reduce_hash(hashed_bytes, step_index, password_length)

            if reduced_password in seen_passwords:
                # Jeśli pojawił się cykl, spróbuj inny wariант redukcji
                reduced_password = reduce_hash(hashed_bytes, (step_index + chain_length) % 256, password_length)

            seen_passwords.add(reduced_password)
            current_password = reduced_password

        return start_password, current_password

    except Exception as error:
        logger.exception(f"Błąd podczas generowania łańcucha tęczowego: {error}")
        raise