#rainbow_des/rainbow/utils.py

import csv
import random
import string
import logging
from typing import List, Tuple, Iterator
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_table_to_csv(table: Iterator[Tuple[str, str]], output_file: str, batch_size: int = 1000) -> None:
    """
    Zapisuje tablicę tęczową do pliku CSV w trybie wsadowym.
    Przyjmuje iterator zamiast listy dla efektywnego wykorzystania pamięci.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['start_password', 'end_password'])
        
        batch = []
        count = 0
        
        for item in table:
            batch.append(item)
            count += 1
            
            if len(batch) >= batch_size:
                writer.writerows(batch)
                logger.info(f"Zapisano {count} łańcuchów")
                batch = []
        
        # Zapisz pozostałe elementy
        if batch:
            writer.writerows(batch)
            logger.info(f"Zapisano {count} łańcuchów")

def load_table_from_csv(input_file: str) -> Iterator[Tuple[str, str]]:
    """
    Wczytuje tablicę tęczową z pliku CSV w trybie strumieniowym.
    """
    with open(input_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row['start_password'], row['end_password']

def validate_password_length(password: str, expected_length: int) -> bool:
    """
    Sprawdza czy hasło ma odpowiednią długość i zawiera tylko dozwolone znaki.
    """
    if len(password) != expected_length:
        return False
    return all(c in string.ascii_lowercase + string.digits for c in password)

def generate_random_passwords(count: int, length: int) -> List[str]:
    """
    Generuje listę losowych haseł o określonej długości.
    Używa tylko małych liter i cyfr.
    """
    alphabet = string.ascii_lowercase + string.digits
    return [''.join(random.choices(alphabet, k=length)) for _ in range(count)]
