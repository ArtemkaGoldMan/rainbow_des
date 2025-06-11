"""
Implementacja tablicy tęczowej do łamania haseł DES.
"""

from .generator_chain import des_hash, generate_chain
from .reduction import reduce_hash
from .crack_hash import crack_hash
from .utils import (
    save_table_to_csv,
    load_table_from_csv,
    validate_password_length,
    generate_random_passwords
)
from .config import (
    PASSWORD_ALPHABET,
    DES_KEY,
    DES_BLOCK_SIZE,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_FILE_SIZE,
    Password,
    Hash,
    Chain,
    Table
)

__all__ = [
    # Funkcje podstawowe
    'des_hash',
    'generate_chain',
    'reduce_hash',
    'crack_hash',
    
    # Funkcje pomocnicze
    'save_table_to_csv',
    'load_table_from_csv',
    'validate_password_length',
    'generate_random_passwords',
    
    # Typy
    'Password',
    'Hash',
    'Chain',
    'Table',
    
    # Stałe
    'PASSWORD_ALPHABET',
    'DES_KEY',
    'DES_BLOCK_SIZE',
    'MIN_PASSWORD_LENGTH',
    'MAX_PASSWORD_LENGTH',
    'MAX_FILE_SIZE'
]
