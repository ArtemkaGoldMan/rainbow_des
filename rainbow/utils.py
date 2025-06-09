#rainbow_des/rainbow/utils.py

"""
Moduł narzędziowy do obsługi tablic tęczowych.
"""

import csv
import random
import logging
import logging.handlers
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

def save_table_to_csv(table: Table, output_file: str, batch_size: int = 1000) -> float:
    """
    Zapisuje tablicę tęczową do pliku CSV w trybie wsadowym.
    Używa iteratora dla efektywności pamięci.
    
    Args:
        table: Iterator krotek (hasło_startowe, hasło_końcowe)
        output_file: Ścieżka do pliku wyjściowego CSV
        batch_size: Rozmiar wsadów zapisu
        
    Returns:
        Całkowity czas trwania w sekundach
        
    Raises:
        ValueError: Jeśli plik wyjściowy jest zbyt duży
        OSError: Jeśli operacje na pliku nie powiodą się
        Exception: Dla innych błędów przetwarzania
    """
    start_time = time.time()
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sprawdzenie czy plik istnieje i jest zbyt duży
        if output_path.exists() and output_path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError(f"Plik wyjściowy przekroczyłby maksymalny rozmiar {MAX_FILE_SIZE} bajtów")
            
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
            
            batch = []
            count = 0
            
            for item in table:
                if not isinstance(item, tuple) or len(item) != 2:
                    logger.warning(f"Nieprawidłowy wpis w tablicy: {item}")
                    continue
                    
                batch.append(item)
                count += 1
                
                if len(batch) >= batch_size:
                    writer.writerows(batch)
                    logger.info(f"Zapisano {count} łańcuchów")
                    batch = []
                    
            if batch:
                writer.writerows(batch)
                logger.info(f"Zapisano {count} łańcuchów (ostatni wsad)")
                
        duration = time.time() - start_time
        logger.info(f"Tablica zapisana w {duration:.2f}s")
        return duration
        
    except Exception as e:
        logger.exception(f"Błąd podczas zapisywania tablicy do pliku CSV: {e}")
        raise

def load_table_from_csv(input_file: str) -> Table:
    """
    Wczytuje tablicę tęczową z pliku CSV w trybie strumieniowym.
    
    Args:
        input_file: Ścieżka do pliku wejściowego CSV
        
    Returns:
        Iterator krotek (hasło_startowe, hasło_końcowe)
        
    Raises:
        FileNotFoundError: Jeśli plik wejściowy nie istnieje
        ValueError: Jeśli format pliku jest nieprawidłowy
        Exception: Dla innych błędów przetwarzania
    """
    try:
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Nie znaleziono pliku tablicy: {input_file}")
            
        if input_path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError(f"Plik wejściowy przekracza maksymalny rozmiar {MAX_FILE_SIZE} bajtów")
            
        with open(input_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            
            # Walidacja nagłówków
            expected_headers = ['hasło_startowe', 'hasło_końcowe']
            if not all(header in reader.fieldnames for header in expected_headers):
                raise ValueError(f"Nieprawidłowe nagłówki CSV. Oczekiwano: {expected_headers}")
                
            for row in reader:
                if all(header in row for header in expected_headers):
                    yield row['hasło_startowe'], row['hasło_końcowe']
                else:
                    logger.warning(f"Pominięto nieprawidłowy wiersz: {row}")
                    
    except Exception as e:
        logger.exception(f"Błąd podczas wczytywania tablicy z pliku CSV: {e}")
        raise

def validate_password_length(password: Password, expected_length: int) -> bool:
    """
    Waliduje długość hasła i zestaw znaków.
    
    Args:
        password: Hasło do walidacji
        expected_length: Oczekiwana długość hasła
        
    Returns:
        True jeśli hasło jest prawidłowe, False w przeciwnym razie
    """
    try:
        if not isinstance(password, str) or not isinstance(expected_length, int):
            return False
            
        if expected_length < MIN_PASSWORD_LENGTH or expected_length > MAX_PASSWORD_LENGTH:
            return False
            
        if len(password) != expected_length:
            logger.debug(f"Hasło '{password}' ma nieprawidłową długość.")
            return False
            
        if not all(c in PASSWORD_ALPHABET for c in password):
            logger.debug(f"Hasło '{password}' zawiera niedozwolone znaki.")
            return False
            
        return True
        
    except Exception as e:
        logger.exception(f"Błąd podczas walidacji hasła: {e}")
        return False

def generate_random_passwords(count: int, length: int, seed: Optional[int] = None) -> Tuple[List[Password], float]:
    """
    Generuje listę losowych haseł o określonej długości.
    Używa tylko małych liter i cyfr.
    
    Args:
        count: Liczba haseł do wygenerowania
        length: Długość każdego hasła
        seed: Opcjonalne ziarno dla generatora liczb losowych
        
    Returns:
        Krotka (lista wygenerowanych haseł, czas trwania w sekundach)
        
    Raises:
        ValueError: Jeśli parametry są nieprawidłowe
        Exception: Dla innych błędów przetwarzania
    """
    start_time = time.time()
    try:
        if not isinstance(count, int) or not isinstance(length, int):
            raise TypeError("Liczba i długość muszą być liczbami całkowitymi")
            
        if count <= 0:
            raise ValueError("Liczba musi być większa od 0")
            
        if length < MIN_PASSWORD_LENGTH or length > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Długość musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
            
        # Inicjalizacja generatora liczb losowych
        if seed is not None:
            random.seed(seed)
            
        # Pre-alokacja listy dla lepszej wydajności
        result = [None] * count
        
        for i in range(count):
            result[i] = ''.join(random.choices(PASSWORD_ALPHABET, k=length))
            
        duration = time.time() - start_time
        logger.info(f"Wygenerowano {count} haseł o długości {length} w {duration:.2f}s")
        return result, duration
        
    except Exception as e:
        logger.exception(f"Błąd podczas generowania losowych haseł: {e}")
        raise
