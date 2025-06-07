#rainbow_des/rainbow/table_builder.py

import multiprocessing
import logging
from typing import List, Tuple, Iterator
from tqdm import tqdm
from .generator_chain import generate_chain
from .utils import validate_password_length

logger = logging.getLogger(__name__)

def _worker_chain(args: Tuple[str, int, int]) -> Tuple[str, str]:
    """
    Funkcja pomocnicza dla multiprocessing.Pool.
    Przyjmuje argumenty jako krotkę i zwraca (start_pwd, end_pwd).
    """
    start_pwd, pwd_length, chain_length = args
    if not validate_password_length(start_pwd, pwd_length):
        raise ValueError(f"Nieprawidłowe hasło startowe: {start_pwd}")
    return generate_chain(start_pwd, pwd_length, chain_length)

def generate_table(
    start_passwords: List[str],
    pwd_length: int,
    chain_length: int,
    num_procs: int,
    batch_size: int = 1000
) -> Iterator[Tuple[str, str]]:
    """
    Równoległe generowanie tablicy tęczowej z obsługą wsadową i raportowaniem postępu.

    Argumenty:
    - start_passwords: lista haseł startowych
    - pwd_length: długość hasła
    - chain_length: długość jednego łańcucha
    - num_procs: liczba procesów
    - batch_size: rozmiar wsadu do przetwarzania

    Zwraca:
    - iterator krotek (start_pwd, end_pwd)
    """
    if not start_passwords:
        raise ValueError("Lista haseł startowych jest pusta")

    if not all(validate_password_length(pwd, pwd_length) for pwd in start_passwords):
        raise ValueError("Niektóre hasła startowe mają nieprawidłową długość lub zawierają niedozwolone znaki")

    logger.info(f"Rozpoczynam generowanie tablicy tęczowej:")
    logger.info(f"- Liczba haseł: {len(start_passwords)}")
    logger.info(f"- Długość hasła: {pwd_length}")
    logger.info(f"- Długość łańcucha: {chain_length}")
    logger.info(f"- Liczba procesów: {num_procs}")
    logger.info(f"- Rozmiar wsadu: {batch_size}")

    # Przygotowanie argumentów dla procesów
    args = [(pwd, pwd_length, chain_length) for pwd in start_passwords]

    # Przetwarzanie wsadowe z paskiem postępu
    with multiprocessing.Pool(processes=num_procs) as pool:
        with tqdm(total=len(start_passwords), desc="Generowanie łańcuchów") as pbar:
            for i in range(0, len(args), batch_size):
                batch_args = args[i:i + batch_size]
                batch_results = pool.map(_worker_chain, batch_args)
                
                for result in batch_results:
                    yield result
                
                pbar.update(len(batch_args))
                logger.info(f"Przetworzono {min(i + batch_size, len(start_passwords))}/{len(start_passwords)} łańcuchów")

    logger.info("Zakończono generowanie tablicy tęczowej")
