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

def crack_hashes_from_file(
    hash_file: str,
    rainbow_table_file: str,
    pwd_length: int,
    chain_length: int
) -> Tuple[int, int]:
    """
    Attempts to crack multiple DES hashes from a file using a rainbow table.
    
    Args:
        hash_file: Path to file containing hashes (one per line in hex)
        rainbow_table_file: Path to the rainbow table file
        pwd_length: Password length
        chain_length: Chain length
        
    Returns:
        Tuple (number of cracked passwords, total number of hashes)
    """
    # Load hashes
    with open(hash_file, 'r') as f:
        hashes = [line.strip() for line in f if line.strip()]

    if not hashes:
        raise ValueError("Hash file is empty")

    # Validate hashes
    target_hashes = []
    for hash_str in hashes:
        try:
            hash_bytes = bytes.fromhex(hash_str)
            if len(hash_bytes) != DES_BLOCK_SIZE:
                print(f"Warning: Skipping invalid hash length: {hash_str}")
                continue
            target_hashes.append(hash_bytes)
        except ValueError:
            print(f"Warning: Skipping invalid hex hash: {hash_str}")

    if not target_hashes:
        raise ValueError("No valid hashes found in file")

    # Load table once
    table, total_rows, unique_endings = load_rainbow_table(rainbow_table_file)
    print(f"Loaded {total_rows} rows, {unique_endings} unique chains")
    print(f"Attempting to crack {len(target_hashes)} hashes...")

    # Crack hashes
    cracked = 0
    start_time = time.time()

    for i, target_hash in enumerate(target_hashes, 1):
        print(f"\nHash {i}/{len(target_hashes)}: {target_hash.hex()}")
        password = crack_single_hash(target_hash, table, pwd_length, chain_length)
        
        if password:
            print(f"Password found: {password}")
            cracked += 1
        else:
            print("Password not found")

    duration = time.time() - start_time
    success_rate = (cracked / len(target_hashes)) * 100

    print(f"\nCracking completed in {duration:.2f}s")
    print(f"Cracked {cracked}/{len(target_hashes)} passwords ({success_rate:.1f}%)")

    return cracked, len(target_hashes)
