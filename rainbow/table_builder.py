#rainbow_des/rainbow/table_builder.py

"""
Moduł do równoległego generowania tablic tęczowych z ulepszoną obsługą błędów i zarządzaniem zasobami.
"""

import multiprocessing
import logging
import logging.handlers
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
    Table,
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

def validate_inputs(
    start_passwords: List[str],
    pwd_length: int,
    chain_length: int,
    num_procs: int,
    batch_size: int
) -> None:
    """
    Waliduje wszystkie parametry wejściowe dla generowania tablicy.
    
    Args:
        start_passwords: Lista haseł startowych
        pwd_length: Oczekiwana długość hasła
        chain_length: Długość każdego łańcucha
        num_procs: Liczba procesów do użycia
        batch_size: Rozmiar wsadów przetwarzania
        
    Raises:
        ValueError: Jeśli którykolwiek parametr jest nieprawidłowy
    """
    if not start_passwords:
        raise ValueError("Lista haseł startowych jest pusta")
    
    if not all(validate_password_length(pwd, pwd_length) for pwd in start_passwords):
        raise ValueError("Niektóre hasła startowe mają nieprawidłową długość lub zawierają niedozwolone znaki")
    
    if pwd_length < MIN_PASSWORD_LENGTH or pwd_length > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Długość hasła musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
    
    if chain_length <= 0:
        raise ValueError("Długość łańcucha musi być większa niż 0")
    
    if num_procs < MIN_PROCESSES or num_procs > MAX_PROCESSES:
        raise ValueError(f"Liczba procesów musi być między {MIN_PROCESSES} a {MAX_PROCESSES}")
    
    if batch_size <= 0:
        raise ValueError("Rozmiar wsadu musi być większy niż 0")

def _worker_chain(args: Tuple[str, int, int, Optional[int]]) -> Chain:
    """
    Funkcja robocza dla multiprocessing.Pool.
    Generuje pojedynczy łańcuch tęczowy.
    
    Args:
        args: Krotka zawierająca (hasło_startowe, długość_hasła, długość_łańcucha, ziarno)
        
    Returns:
        Krotka (hasło_startowe, hasło_końcowe)
        
    Raises:
        ValueError: Jeśli walidacja wejścia nie powiedzie się
        Exception: Dla innych błędów przetwarzania
    """
    start_pwd, pwd_length, chain_length, seed = args
    try:
        # Inicjalizacja ziarna dla tego procesu
        if seed is not None:
            random.seed(seed + os.getpid())
            
        if not validate_password_length(start_pwd, pwd_length):
            raise ValueError(f"Nieprawidłowe hasło startowe: {start_pwd}")
            
        result = generate_chain(start_pwd, pwd_length, chain_length)
        logger.debug(f"[worker] {start_pwd} → {result[1]}")
        return result
        
    except Exception as e:
        logger.exception(f"Błąd podczas generowania łańcucha dla '{start_pwd}': {e}")
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
    Generuje tablicę tęczową równolegle z ulepszoną obsługą błędów i zarządzaniem zasobami.
    
    Args:
        start_passwords: Lista haseł startowych
        pwd_length: Długość haseł
        chain_length: Długość każdego łańcucha
        num_procs: Liczba procesów do użycia
        seed: Opcjonalne ziarno dla generatora liczb losowych
        batch_size: Rozmiar wsadów przetwarzania
        timeout: Maksymalny czas w sekundach dla przetwarzania
        
    Returns:
        Krotka (iterator krotek (hasło_startowe, hasło_końcowe), czas trwania w sekundach)
        
    Raises:
        ValueError: Jeśli walidacja wejścia nie powiedzie się
        TimeoutError: Jeśli przetwarzanie zajmie zbyt dużo czasu
        Exception: Dla innych błędów przetwarzania
    """
    start_time = time.time()
    results = []
    
    try:
        # Walidacja wszystkich wejść
        validate_inputs(start_passwords, pwd_length, chain_length, num_procs, batch_size)
        
        logger.info(f"Rozpoczynam generowanie tablicy tęczowej:")
        logger.info(f"- Liczba haseł: {len(start_passwords)}")
        logger.info(f"- Długość hasła: {pwd_length}")
        logger.info(f"- Długość łańcucha: {chain_length}")
        logger.info(f"- Liczba procesów: {num_procs}")
        logger.info(f"- Rozmiar wsadu: {batch_size}")
        if seed is not None:
            logger.info(f"- Używam ziarna: {seed}")
            
        args = [(pwd, pwd_length, chain_length, seed) for pwd in start_passwords]
        
        with multiprocessing.Pool(processes=num_procs) as pool:
            with tqdm(total=len(start_passwords), desc="Generowanie łańcuchów") as pbar:
                for i in range(0, len(args), batch_size):
                    # Sprawdzenie limitu czasu
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Przekroczono limit czasu ({timeout} sekund)")
                        
                    batch_args = args[i:i + batch_size]
                    
                    try:
                        # Przetwarzanie wsadu z limitem czasu
                        batch_results = pool.map_async(_worker_chain, batch_args)
                        batch_results = batch_results.get(timeout=timeout - (time.time() - start_time))
                        
                        for result in batch_results:
                            results.append(result)
                            
                    except multiprocessing.TimeoutError:
                        raise TimeoutError(f"Przekroczono limit czasu dla wsadu {i}-{i + batch_size}")
                    except Exception as e:
                        logger.error(f"Błąd w przetwarzaniu wsadu {i}-{i + batch_size}: {e}")
                        raise
                        
                    pbar.update(len(batch_args))
                    logger.debug(f"Przetworzono {min(i + batch_size, len(start_passwords))}/{len(start_passwords)} łańcuchów")
                    
        duration = time.time() - start_time
        logger.info(f"Zakończono generowanie tablicy tęczowej w {duration:.2f}s")
        return results, duration
        
    except Exception as e:
        logger.exception(f"Nie udało się wygenerować tablicy: {e}")
        raise
