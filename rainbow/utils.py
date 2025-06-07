#rainbow_des/rainbow/utils.py

import csv
import random
import string
import logging
from typing import List, Tuple, Iterator
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def save_table_to_csv(table: Iterator[Tuple[str, str]], output_file: str, batch_size: int = 1000) -> None:
    """
    Zapisuje tablicę tęczową do pliku CSV w trybie wsadowym.
    Przyjmuje iterator zamiast listy dla efektywnego wykorzystania pamięci.
    """
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['start_password', 'end_password'])

            batch = []
            count = 0

            for item in table:
                if not isinstance(item, tuple) or len(item) != 2:
                    logger.warning(f"Nieprawidłowy rekord w tablicy: {item}")
                    continue

                batch.append(item)
                count += 1

                if len(batch) >= batch_size:
                    writer.writerows(batch)
                    logger.info(f"Zapisano {count} łańcuchów")
                    batch = []

            if batch:
                writer.writerows(batch)
                logger.info(f"Zapisano {count} łańcuchów (ostatnia partia)")

    except Exception as e:
        logger.exception(f"Błąd podczas zapisu tablicy do pliku CSV: {e}")
        raise

def load_table_from_csv(input_file: str) -> Iterator[Tuple[str, str]]:
    """
    Wczytuje tablicę tęczową z pliku CSV w trybie strumieniowym.
    """
    try:
        with open(input_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'start_password' in row and 'end_password' in row:
                    yield row['start_password'], row['end_password']
                else:
                    logger.warning(f"Pominięto nieprawidłowy wiersz: {row}")
    except FileNotFoundError:
        logger.error(f"Plik {input_file} nie został znaleziony.")
        raise
    except Exception as e:
        logger.exception(f"Błąd podczas wczytywania tablicy z pliku: {e}")
        raise

def validate_password_length(password: str, expected_length: int) -> bool:
    """
    Sprawdza czy hasło ma odpowiednią długość i zawiera tylko dozwolone znaki.
    """
    if len(password) != expected_length:
        logger.debug(f"Hasło '{password}' ma nieprawidłową długość.")
        return False
    if not all(c in string.ascii_lowercase + string.digits for c in password):
        logger.debug(f"Hasło '{password}' zawiera niedozwolone znaki.")
        return False
    return True

def generate_random_passwords(count: int, length: int) -> List[str]:
    """
    Generuje listę losowych haseł o określonej długości.
    Używa tylko małych liter i cyfr.
    """
    if count <= 0 or length <= 0:
        logger.error("Liczba lub długość haseł musi być większa niż 0.")
        raise ValueError("Nieprawidłowe parametry wejściowe.")

    alphabet = string.ascii_lowercase + string.digits
    result = [''.join(random.choices(alphabet, k=length)) for _ in range(count)]
    logger.info(f"Wygenerowano {count} haseł o długości {length}")
    return result
