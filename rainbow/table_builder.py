import multiprocessing
from .generator_chain import generate_chain

def _worker_chain(args: tuple[str, int, int]) -> tuple[str, str]:
    """
    Funkcja pomocnicza dla multiprocessing.Pool.
    Przyjmuje argumenty jako krotkę i zwraca (start_pwd, end_pwd).
    """
    return generate_chain(*args)

def generate_table(
    start_passwords: list[str],
    pwd_length: int,
    chain_length: int,
    num_procs: int
) -> list[tuple[str, str]]:
    """
    Równoległe generowanie tablicy tęczowej.

    Argumenty:
    - start_passwords: lista haseł startowych (np. wygenerowanych losowo)
    - pwd_length: długość hasła (np. 6)
    - chain_length: długość jednego łańcucha (L)
    - num_procs: liczba procesów (rdzeni CPU do wykorzystania)

    Zwraca:
    - lista krotek (start_pwd, end_pwd)
    """
    # Przygotowanie listy argumentów dla każdego procesu
    args = [(pwd, pwd_length, chain_length) for pwd in start_passwords]

    # Uruchomienie multiprocessing.Pool z równoległą mapą
    with multiprocessing.Pool(processes=num_procs) as pool:
        result = pool.map(_worker_chain, args)

    return result
