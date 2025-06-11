# rainbow_des/rainbow/generator_chain.py

"""
Module for generating rainbow chains and reduction functions.
"""

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
    Chain
)

def des_hash(password: Password) -> Hash:
    """
    Generates DES hash for the given password.

    Args:
        password: Password to hash

    Returns:
        DES hash as bytes

    Raises:
        ValueError: If password is invalid
        Exception: For other processing errors
    """
    try:
        if not isinstance(password, str):
            raise TypeError("Password must be a string")

        if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}")

        data_bytes = password.encode('utf-8')
        padded_data = pad(data_bytes, DES_BLOCK_SIZE)
        cipher = DES.new(DES_KEY, DES.MODE_ECB)
        encrypted_bytes = cipher.encrypt(padded_data)

        return encrypted_bytes[:DES_BLOCK_SIZE]

    except Exception as error:
        raise


def generate_chain(start_password: Password, password_length: int, chain_length: int) -> Chain:
    """
    Generates a rainbow chain starting from the given password.

    Args:
        start_password: Starting password
        password_length: Password length
        chain_length: Chain length

    Returns:
        Tuple (start_password, end_password)

    Raises:
        ValueError: If parameters are invalid
        Exception: For other processing errors
    """
    try:
        if not isinstance(start_password, str):
            raise TypeError("Starting password must be a string")

        if len(start_password) != password_length:
            raise ValueError(f"Starting password must have length {password_length}")

        if chain_length <= 0:
            raise ValueError("Chain length must be greater than 0")

        current_password = start_password
        seen_passwords = {current_password}

        for step_index in range(chain_length):
            hashed_bytes = des_hash(current_password)
            reduced_password = reduce_hash(hashed_bytes, step_index, password_length)

            if reduced_password in seen_passwords:
                # If a cycle is detected, try a different reduction variant
                reduced_password = reduce_hash(hashed_bytes, (step_index + chain_length) % 256, password_length)

            seen_passwords.add(reduced_password)
            current_password = reduced_password

        return start_password, current_password

    except Exception as error:
        raise