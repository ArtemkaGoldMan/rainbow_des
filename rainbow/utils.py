#rainbow_des/rainbow/utils.py

"""
Utility module for handling rainbow tables.
"""

import csv
import random
import os
import time
from typing import List, Tuple, Iterator, Optional
from pathlib import Path

from .config import (
    PASSWORD_ALPHABET,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    CSV_HEADERS,
    MAX_FILE_SIZE,
    Password,
    Chain,
    Table
)

def save_table_to_csv(table: Table, output_file: str, batch_size: int = 1000) -> float:
    """
    Saves rainbow table to CSV file in batch mode.
    Uses iterator for memory efficiency.
    
    Args:
        table: Iterator of (start_password, end_password) tuples
        output_file: Path to output CSV file
        batch_size: Write batch size
        
    Returns:
        Total duration in seconds
        
    Raises:
        ValueError: If output file would be too large
        OSError: If file operations fail
        Exception: For other processing errors
    """
    start_time = time.time()
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists and would be too large
        if output_path.exists() and output_path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError(f"Output file would exceed maximum size of {MAX_FILE_SIZE} bytes")
            
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
            
            batch = []
            count = 0
            
            for item in table:
                if not isinstance(item, tuple) or len(item) != 2:
                    continue
                    
                batch.append(item)
                count += 1
                
                if len(batch) >= batch_size:
                    writer.writerows(batch)
                    batch = []
                    
            if batch:
                writer.writerows(batch)
                
        duration = time.time() - start_time
        return duration
        
    except Exception as e:
        raise

def load_table_from_csv(input_file: str) -> Table:
    """
    Loads rainbow table from CSV file in streaming mode.
    
    Args:
        input_file: Path to input CSV file
        
    Returns:
        Iterator of (start_password, end_password) tuples
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If file format is invalid
        Exception: For other processing errors
    """
    try:
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Table file not found: {input_file}")
            
        if input_path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError(f"Input file exceeds maximum size of {MAX_FILE_SIZE} bytes")
            
        with open(input_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            expected_headers = ['start_password', 'end_password']
            if not all(header in reader.fieldnames for header in expected_headers):
                raise ValueError(f"Invalid CSV headers. Expected: {expected_headers}")
                
            for row in reader:
                if all(header in row for header in expected_headers):
                    yield row['start_password'], row['end_password']
                    
    except Exception as e:
        raise

def validate_password_length(password: Password, expected_length: int) -> bool:
    """
    Validates password length and character set.
    
    Args:
        password: Password to validate
        expected_length: Expected password length
        
    Returns:
        True if password is valid, False otherwise
    """
    try:
        if not isinstance(password, str) or not isinstance(expected_length, int):
            return False
            
        if expected_length < MIN_PASSWORD_LENGTH or expected_length > MAX_PASSWORD_LENGTH:
            return False
            
        if len(password) != expected_length:
            return False
            
        if not all(c in PASSWORD_ALPHABET for c in password):
            return False
            
        return True
        
    except Exception as e:
        return False

def generate_random_passwords(count: int, length: int, seed: Optional[int] = None) -> Tuple[List[Password], float]:
    """
    Generates a list of random passwords of specified length.
    Uses only lowercase letters and digits.
    
    Args:
        count: Number of passwords to generate
        length: Length of each password
        seed: Optional seed for random number generator
        
    Returns:
        Tuple (list of generated passwords, duration in seconds)
        
    Raises:
        ValueError: If parameters are invalid
        Exception: For other processing errors
    """
    start_time = time.time()
    try:
        if not isinstance(count, int) or not isinstance(length, int):
            raise TypeError("Count and length must be integers")
            
        if count <= 0:
            raise ValueError("Count must be greater than 0")
            
        if length < MIN_PASSWORD_LENGTH or length > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}")
            
        # Initialize random number generator
        if seed is not None:
            random.seed(seed)
            
        # Pre-allocate list for better performance
        result = [None] * count
        
        for i in range(count):
            result[i] = ''.join(random.choices(PASSWORD_ALPHABET, k=length))
            
        duration = time.time() - start_time
        return result, duration
        
    except Exception as e:
        raise
