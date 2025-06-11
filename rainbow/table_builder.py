#rainbow_des/rainbow/table_builder.py

"""
Module for parallel generation of rainbow tables with improved error handling and resource management.
"""

import multiprocessing
import os
import random
import time
from typing import List, Tuple, Iterator, Optional
from pathlib import Path
from tqdm import tqdm

from .generator_chain import generate_chain
from .utils import validate_password_length
from .config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_TIMEOUT,
    MIN_PROCESSES,
    MAX_PROCESSES,
    MAX_FILE_SIZE,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    Chain,
    Table
)

def validate_inputs(
    start_passwords: List[str],
    pwd_length: int,
    chain_length: int,
    num_procs: int,
    batch_size: int
) -> None:
    """
    Validates all input parameters for table generation.
    
    Args:
        start_passwords: List of starting passwords
        pwd_length: Expected password length
        chain_length: Length of each chain
        num_procs: Number of processes to use
        batch_size: Processing batch size
        
    Raises:
        ValueError: If any parameter is invalid
    """
    if not start_passwords:
        raise ValueError("List of starting passwords is empty")
    
    if not all(validate_password_length(pwd, pwd_length) for pwd in start_passwords):
        raise ValueError("Some starting passwords have invalid length or contain disallowed characters")
    
    if pwd_length < MIN_PASSWORD_LENGTH or pwd_length > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}")
    
    if chain_length <= 0:
        raise ValueError("Chain length must be greater than 0")
    
    if num_procs < MIN_PROCESSES or num_procs > MAX_PROCESSES:
        raise ValueError(f"Number of processes must be between {MIN_PROCESSES} and {MAX_PROCESSES}")
    
    if batch_size <= 0:
        raise ValueError("Batch size must be greater than 0")

def _worker_chain(args: Tuple[str, int, int, Optional[int]]) -> Chain:
    """
    Worker function for multiprocessing.Pool.
    Generates a single rainbow chain.
    
    Args:
        args: Tuple containing (start_password, password_length, chain_length, seed)
        
    Returns:
        Tuple (start_password, end_password)
        
    Raises:
        ValueError: If input validation fails
        Exception: For other processing errors
    """
    start_pwd, pwd_length, chain_length, seed = args
    try:
        # Initialize seed for this process
        if seed is not None:
            random.seed(seed + os.getpid())
            
        if not validate_password_length(start_pwd, pwd_length):
            raise ValueError(f"Invalid starting password: {start_pwd}")
            
        result = generate_chain(start_pwd, pwd_length, chain_length)
        return result
        
    except Exception as e:
        raise

def generate_table(
    start_passwords: List[str],
    pwd_length: int,
    chain_length: int,
    num_procs: int,
    seed: Optional[int] = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    timeout: int = DEFAULT_TIMEOUT
) -> Tuple[Table, float]:
    """
    Generates a rainbow table in parallel with improved error handling and resource management.
    
    Args:
        start_passwords: List of starting passwords
        pwd_length: Password length
        chain_length: Length of each chain
        num_procs: Number of processes to use
        seed: Optional seed for random number generator
        batch_size: Processing batch size
        timeout: Maximum time in seconds for processing
        
    Returns:
        Tuple (iterator of (start_password, end_password) tuples, duration in seconds)
        
    Raises:
        ValueError: If input validation fails
        TimeoutError: If processing takes too long
        Exception: For other processing errors
    """
    start_time = time.time()
    results = []
    
    try:
        # Validate all inputs
        validate_inputs(start_passwords, pwd_length, chain_length, num_procs, batch_size)
        
        args = [(pwd, pwd_length, chain_length, seed) for pwd in start_passwords]
        
        with multiprocessing.Pool(processes=num_procs) as pool:
            with tqdm(total=len(start_passwords), desc="Generating chains") as pbar:
                for i in range(0, len(args), batch_size):
                    # Check timeout limit
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Timeout limit exceeded ({timeout} seconds)")
                        
                    batch_args = args[i:i + batch_size]
                    
                    try:
                        # Process batch with timeout
                        batch_results = pool.map_async(_worker_chain, batch_args)
                        batch_results = batch_results.get(timeout=timeout - (time.time() - start_time))
                        
                        for result in batch_results:
                            results.append(result)
                            
                    except multiprocessing.TimeoutError:
                        raise TimeoutError(f"Timeout exceeded for batch {i}-{i + batch_size}")
                    except Exception as e:
                        raise
                        
                    pbar.update(len(batch_args))
                    
        duration = time.time() - start_time
        return results, duration
        
    except Exception as e:
        raise
