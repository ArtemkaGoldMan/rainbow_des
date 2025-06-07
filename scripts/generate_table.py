# rainbow_des/scripts/generate_table.py

import argparse
import sys
import os
import logging
from pathlib import Path
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rainbow.table_builder import generate_table
from rainbow.utils import generate_random_passwords, save_table_to_csv

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generowanie tablicy tęczowej dla algorytmu DES.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=1000,
        help="Ilość haseł startowych"
    )
    parser.add_argument(
        "--length", "-l",
        type=int,
        default=6,
        help="Długość hasła"
    )
    parser.add_argument(
        "--chain", "-c",
        type=int,
        default=1000,
        help="Długość łańcucha"
    )
    parser.add_argument(
        "--procs", "-p",
        type=int,
        default=os.cpu_count(),
        help="Liczba procesów"
    )
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=1000,
        help="Rozmiar wsadu do przetwarzania"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="rainbow_table.csv",
        help="Plik wynikowy CSV"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        help="Ziarno dla generatora liczb losowych"
    )
    
    return parser.parse_args()

def main():
    args = parse_args()

    # Ініціалізація логів
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Перевірка аргументів
    if args.count <= 0:
        logger.error("Ilość haseł musi być większa niż 0")
        sys.exit(1)
    if args.length <= 0 or args.length > 8:
        logger.error("Długość hasła musi być w zakresie 1–8")
        sys.exit(1)
    if args.chain <= 0:
        logger.error("Długość łańcucha musi być większa niż 0")
        sys.exit(1)
    if args.procs <= 0:
        logger.error("Liczba procesów musi być większa niż 0")
        sys.exit(1)

    if args.seed is not None:
        random.seed(args.seed)

    try:
        logger.info(f"Generowanie {args.count} losowych haseł o długości {args.length}")
        start_passwords = generate_random_passwords(args.count, args.length)

        table = generate_table(
            start_passwords=start_passwords,
            pwd_length=args.length,
            chain_length=args.chain,
            num_procs=args.procs,
            batch_size=args.batch_size
        )

        output_path = Path(args.output)
        if output_path.exists():
            logger.warning(f"Plik {output_path} już istnieje i zostanie nadpisany.")

        logger.info(f"Zapisuję tablicę tęczową do {output_path}")
        save_table_to_csv(table, output_path, batch_size=args.batch_size)
        logger.info("Zakończono generowanie tablicy tęczowej")

    except KeyboardInterrupt:
        logger.error("Przerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Wystąpił błąd krytyczny: {e}")
        sys.exit(1)

    args = parse_args()
    
    # Konfiguracja generatora liczb losowych
    if args.seed is not None:
        random.seed(args.seed)
    
    try:
        # Generowanie losowych haseł startowych
        logger.info(f"Generowanie {args.count} losowych haseł o długości {args.length}")
        start_passwords = generate_random_passwords(args.count, args.length)
        
        # Generowanie tablicy tęczowej
        table = generate_table(
            start_passwords=start_passwords,
            pwd_length=args.length,
            chain_length=args.chain,
            num_procs=args.procs,
            batch_size=args.batch_size
        )
        
        # Zapis do pliku
        output_path = Path(args.output)
        logger.info(f"Zapisuję tablicę tęczową do {output_path}")
        save_table_to_csv(table, output_path, batch_size=args.batch_size)
        
        logger.info("Zakończono generowanie tablicy tęczowej")
        
    except KeyboardInterrupt:
        logger.error("Przerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Wystąpił błąd: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
