# rainbow_des/scripts/des_tool.py

"""
Narzędzie wiersza poleceń do generowania tablic tęczowych i łamania hasł DES.
"""

import argparse
import sys
import os
import logging
from pathlib import Path
import random
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rainbow.crack_hash import crack_hash
from rainbow.generator_chain import des_hash
from rainbow.table_builder import generate_table
from rainbow.utils import generate_random_passwords, save_table_to_csv, validate_password_length
from rainbow.config import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    DES_BLOCK_SIZE,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CHAIN_LENGTH,
    DEFAULT_NUM_CHAINS,
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="System do generowania tablic tęczowych i łamania hasł DES.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Dostępne komendy')

    # hash
    hash_parser = subparsers.add_parser('hash', help='Generuje hash z hasła')
    hash_parser.add_argument("--password", "-p", type=str, required=True, help="Hasło do zahashowania")
    hash_parser.add_argument("--length", "-l", type=int, default=3, help="Długość hasła (domyślnie 3)")

    # generate
    generate_parser = subparsers.add_parser('generate', help='Generuje tablicę tęczową')
    generate_parser.add_argument("--chains", "-n", type=int, required=True, 
                               help=f"Liczba łańcuchów (domyślnie: {DEFAULT_NUM_CHAINS})")
    generate_parser.add_argument("--length", "-l", type=int, required=True, help="Długość hasła")
    generate_parser.add_argument("--chain-length", "-c", type=int, required=True,
                               help=f"Długość łańcucha (domyślnie: {DEFAULT_CHAIN_LENGTH})")
    generate_parser.add_argument("--procs", "-p", type=int, default=os.cpu_count(), help="Liczba procesów")
    generate_parser.add_argument("--batch-size", "-b", type=int, default=DEFAULT_BATCH_SIZE, 
                               help=f"Rozmiar wsadu (domyślnie: {DEFAULT_BATCH_SIZE})")
    generate_parser.add_argument("--seed", type=int, help="Ziarno dla generatora liczb losowych")
    generate_parser.add_argument("--output", "-o", type=str, required=True, help="Plik wynikowy CSV")

    # crack
    crack_parser = subparsers.add_parser('crack', help='Próbuje złamać hash')
    crack_parser.add_argument("--hash", "-H", type=str, required=True, help="Hash do złamania (hex)")
    crack_parser.add_argument("--table", "-t", type=str, required=True, help="Plik z tablicą tęczową")
    crack_parser.add_argument("--length", "-l", type=int, required=True, help="Długość hasła")
    crack_parser.add_argument("--chain-length", "-c", type=int, required=True, help="Długość łańcucha")

    return parser.parse_args()


def hash_command(args):
    """Obsługa komendy hash"""
    try:
        if not validate_password_length(args.password, args.length):
            logger.error(f"Hasło musi mieć dokładnie {args.length} znaków i zawierać tylko małe litery i cyfry")
            sys.exit(1)

        hash_bytes = des_hash(args.password)
        print(f"Hash: {hash_bytes.hex()}")
        print("\nUżyj tego hasha z komendą crack:")
        print(f"python scripts/des_tool.py crack --hash {hash_bytes.hex()} --table <twoja_tablica.csv> --length {args.length} --chain-length <długość_łańcucha>")
    except Exception as e:
        logger.exception(f"Błąd podczas generowania hasha: {e}")
        sys.exit(1)


def generate_command(args):
    """Obsługa komendy generate"""
    try:
        # Walidacja parametrów
        if args.length < MIN_PASSWORD_LENGTH or args.length > MAX_PASSWORD_LENGTH:
            print(f"Błąd: Długość hasła musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
            logger.error(f"Długość hasła musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
            sys.exit(1)
            
        if args.chains <= 0:
            print("Błąd: Liczba łańcuchów musi być większa od 0")
            logger.error("Liczba łańcuchów musi być większa od 0")
            sys.exit(1)
            
        if args.chain_length <= 0:
            print("Błąd: Długość łańcucha musi być większa od 0")
            logger.error("Długość łańcucha musi być większa od 0")
            sys.exit(1)
            
        if args.procs <= 0:
            print("Błąd: Liczba procesów musi być większa od 0")
            logger.error("Liczba procesów musi być większa od 0")
            sys.exit(1)
            
        if args.batch_size <= 0:
            print("Błąd: Rozmiar wsadu musi być większy od 0")
            logger.error("Rozmiar wsadu musi być większy od 0")
            sys.exit(1)

        print("\nRozpoczynam generowanie tablicy tęczowej:")
        print(f"- Liczba łańcuchów: {args.chains}")
        print(f"- Długość hasła: {args.length}")
        print(f"- Długość łańcucha: {args.chain_length}")
        print(f"- Liczba procesów: {args.procs}")
        print(f"- Rozmiar wsadu: {args.batch_size}")
        if args.seed is not None:
            print(f"- Ziarno: {args.seed}")
        print(f"- Plik wyjściowy: {args.output}")
        print("\nGenerowanie losowych haseł...")

        # Generowanie losowych haseł
        logger.info("Generowanie losowych haseł...")
        passwords, pwd_gen_time = generate_random_passwords(
            args.chains,
            args.length,
            args.seed
        )
        print(f"Wygenerowano {len(passwords)} haseł w {pwd_gen_time:.6f}s")
        logger.info(f"Wygenerowano {len(passwords)} haseł w {pwd_gen_time:.6f}s")
        
        # Generowanie tablicy tęczowej
        print("\nGenerowanie tablicy tęczowej...")
        logger.info("Generowanie tablicy tęczowej...")
        table, table_gen_time = generate_table(
            passwords,
            args.length,
            args.chain_length,
            args.procs,
            args.seed,
            args.batch_size
        )
        print(f"Wygenerowano tablicę tęczową w {table_gen_time:.6f}s")
        logger.info(f"Wygenerowano tablicę tęczową w {table_gen_time:.6f}s")
        
        # Obliczanie statystyk unikalności
        total_chains = len(table)
        unique_chains = len(set(end_pwd for _, end_pwd in table))
        unique_percentage = (unique_chains / total_chains) * 100
        
        
        # Zapisywanie do pliku
        print(f"\nZapisywanie tablicy do pliku {args.output}...")
        logger.info(f"Zapisywanie tablicy do pliku {args.output}...")
        save_time = save_table_to_csv(table, args.output)
        print(f"Zapisano tablicę w {save_time:.6f}s")
        logger.info(f"Zapisano tablicę w {save_time:.6f}s")
        
        # Wyświetlanie podsumowania
        print("\nPodsumowanie:")
        print(f"- Całkowita liczba łańcuchów: {total_chains}")
        print(f"- Unikalnych łańcuchów: {unique_chains}")
        print(f"- Procent unikalności: {unique_percentage:.2f}%")
        print(f"- Długość hasła: {args.length}")
        print(f"- Długość łańcucha: {args.chain_length}")
        print(f"- Liczba procesów: {args.procs}")
        print(f"- Rozmiar wsadu: {args.batch_size}")
        print(f"- Czas generowania haseł: {pwd_gen_time:.6f}s")
        print(f"- Czas generowania tablicy: {table_gen_time:.6f}s")
        print(f"- Czas zapisu: {save_time:.6f}s")
        print(f"- Całkowity czas: {pwd_gen_time + table_gen_time + save_time:.6f}s")
        
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
        logger.error("Przerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print(f"\nBłąd podczas generowania tablicy: {e}")
        logger.exception(f"Błąd podczas generowania tablicy: {e}")
        sys.exit(1)


def crack_command(args):
    """Obsługa komendy crack"""
    try:
        # Walidacja formatu hasha
        try:
            target_hash = bytes.fromhex(args.hash)
            if len(target_hash) != DES_BLOCK_SIZE:
                raise ValueError(f"Hash musi mieć dokładnie {DES_BLOCK_SIZE} bajtów ({DES_BLOCK_SIZE * 2} znaków hex)")
        except ValueError as e:
            logger.error(f"Nieprawidłowy format hasha: {e}")
            sys.exit(1)

        # Walidacja pliku tablicy
        table_path = Path(args.table)
        if not table_path.exists():
            logger.error(f"Plik z tablicą tęczową nie istnieje: {args.table}")
            sys.exit(1)
        if table_path.stat().st_size < 32:
            logger.warning("Plik tablicy wygląda na bardzo mały – możliwe, że jest niekompletny")

        # Walidacja parametrów
        if args.length < MIN_PASSWORD_LENGTH or args.length > MAX_PASSWORD_LENGTH:
            logger.error(f"Długość hasła musi być między {MIN_PASSWORD_LENGTH} a {MAX_PASSWORD_LENGTH}")
            sys.exit(1)
            
        if args.chain_length <= 0:
            logger.error("Długość łańcucha musi być większa od 0")
            sys.exit(1)

        logger.info(f"Próba złamania hasha: {args.hash}")
        logger.info(f"Używam tablicy tęczowej: {args.table}")

        start_time = time.time()
        password = crack_hash(
            target_hash=target_hash,
            rainbow_table_file=args.table,
            pwd_length=args.length,
            chain_length=args.chain_length
        )
        crack_duration = time.time() - start_time

        if password:
            logger.info(f"Znaleziono hasło: {password}")
            verify_start = time.time()
            if des_hash(password) == target_hash:
                verify_duration = time.time() - verify_start
                logger.info(f"Weryfikacja hasła pomyślna (czas: {verify_duration:.2f}s)")
            else:
                verify_duration = time.time() - verify_start
                logger.error(f"Błąd weryfikacji hasła! (czas: {verify_duration:.2f}s)")
        else:
            logger.error("Nie znaleziono hasła")
            
        logger.info(f"\n=== Statystyki łamania hasha ===")
        logger.info(f"Całkowity czas: {crack_duration:.2f}s")
        if password:
            logger.info(f"Czas weryfikacji: {verify_duration:.2f}s")
            
    except Exception as e:
        logger.exception(f"Wystąpił błąd podczas łamania hasha: {e}")
        sys.exit(1)


def main():
    """Główny punkt wejścia"""
    args = parse_args()

    if args.command == 'hash':
        hash_command(args)
    elif args.command == 'generate':
        generate_command(args)
    elif args.command == 'crack':
        crack_command(args)
    else:
        logger.error("Nie wybrano komendy. Użyj --help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
