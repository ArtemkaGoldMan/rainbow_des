"""
Module for cracking DES passwords using rainbow tables.
"""

import os
import time
import csv
from typing import Optional, List, Dict, Tuple
from pathlib import Path

from .generator_chain import des_hash
from .reduction import reduce_hash
from .utils import load_table_from_csv
from .config import (
    DES_BLOCK_SIZE,
    Password,
    Hash
)

def load_rainbow_table(rainbow_table_file: str) -> Tuple[Dict[str, str], int, int]:
    """
    Loads rainbow table from file and returns it as a dictionary.
    
    Args:
        rainbow_table_file: Path to the rainbow table file
        
    Returns:
        Tuple (table dictionary, total rows, unique endings)
    """
    table_path = Path(rainbow_table_file)
    if not table_path.exists():
        raise FileNotFoundError(f"Table file not found: {rainbow_table_file}")

    table = {}
    total_rows = 0
    unique_endings = 0

    for start_pwd, end_pwd in load_table_from_csv(rainbow_table_file):
        total_rows += 1
        if end_pwd not in table:
            table[end_pwd] = start_pwd
            unique_endings += 1

    return table, total_rows, unique_endings

def crack_single_hash(
    target_hash: Hash,
    table: Dict[str, str],
    pwd_length: int,
    chain_length: int
) -> Optional[Password]:
    """
    Attempts to crack a single DES hash using a pre-loaded rainbow table.
    
    Args:
        target_hash: Hash to crack
        table: Pre-loaded rainbow table
        pwd_length: Password length
        chain_length: Chain length
        
    Returns:
        Found password or None if not found
    """
    for step in range(chain_length - 1, -1, -1):
        current_hash = target_hash

        for i in range(step, chain_length):
            pwd_candidate = reduce_hash(current_hash, i, pwd_length)
            current_hash = des_hash(pwd_candidate)

        if pwd_candidate in table:
            start_pwd = table[pwd_candidate]
            test_pwd = start_pwd

            for i in range(chain_length):
                if des_hash(test_pwd) == target_hash:
                    return test_pwd

                test_pwd = reduce_hash(des_hash(test_pwd), i, pwd_length)

    return None

def crack_hash(
    target_hash: Hash,
    rainbow_table_file: str,
    pwd_length: int,
    chain_length: int
) -> Optional[Password]:
    """
    Attempts to crack a DES hash using a rainbow table.
    
    Args:
        target_hash: Hash to crack
        rainbow_table_file: Path to the rainbow table file
        pwd_length: Password length
        chain_length: Chain length
        
    Returns:
        Found password or None if not found
    """
    # Load table
    table, total_rows, unique_endings = load_rainbow_table(rainbow_table_file)
    print(f"Loaded {total_rows} rows, {unique_endings} unique chains")

    crack_start = time.time()
    password = crack_single_hash(target_hash, table, pwd_length, chain_length)
    duration = time.time() - crack_start

    if password:
        print(f"Password found: {password}")
        print(f"Cracking time: {duration:.6f}s")
    else:
        print("Password not found")
        print(f"Cracking time: {duration:.6f}s")

    return password