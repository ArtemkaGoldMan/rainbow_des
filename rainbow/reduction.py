"""
Module implementing reduction functions for rainbow tables.
"""

import hashlib
from .config import (
    PASSWORD_ALPHABET,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    Password,
    Hash
)

def reduce_hash(hash_bytes: Hash, step: int, pwd_length: int) -> Password:
    """
    Reduces DES hash to a password of specified length using SHA-256 as a mixing function.
    
    Args:
        hash_bytes: Hash to reduce
        step: Step number in the chain
        pwd_length: Length of the output password
        
    Returns:
        Password as a string containing only characters from PASSWORD_ALPHABET
    """
    if not isinstance(hash_bytes, bytes):
        raise TypeError("Hash must be bytes")
        
    if pwd_length < MIN_PASSWORD_LENGTH or pwd_length > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}")
    
    # Mixing data: hash + step number
    data = hash_bytes + step.to_bytes(4, byteorder='big')
    digest = hashlib.sha256(data).digest()

    alphabet_size = len(PASSWORD_ALPHABET)
    password = ''.join(
        PASSWORD_ALPHABET[b % alphabet_size]
        for b in digest[:pwd_length]
    )

    return password
