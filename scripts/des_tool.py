#!/usr/bin/env python3

import argparse
import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rainbow.crack_hash import crack_hash
from rainbow.generator_chain import des_hash
from rainbow.table_builder import generate_table
from rainbow.utils import generate_random_passwords, save_table_to_csv

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        description="System do generowania tablic tęczowych i łamania haseł DES.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Podkomendy
    subparsers = parser.add_subparsers(dest='command', help='Dostępne komendy')
    
    # Komenda hash
    hash_parser = subparsers.add_parser('hash', help='Generuje hash z hasła')
    hash_parser.add_argument(
        "--password", "-p",
        type=str,
        required=True,
        help="Hasło do zahashowania"
    )
    hash_parser.add_argument(
        "--length", "-l",
        type=int,
        default=3,
        help="Długość hasła (domyślnie 3)"
    )
    
    # Komenda generate
    generate_parser = subparsers.add_parser('generate', help='Generuje tablicę tęczową')
    generate_parser.add_argument(
        "--chains", "-n",
        type=int,
        required=True,
        help="Liczba łańcuchów do wygenerowania"
    )
    generate_parser.add_argument(
        "--length", "-l",
        type=int,
        required=True,
        help="Długość hasła"
    )
    generate_parser.add_argument(
        "--chain-length", "-c",
        type=int,
        required=True,
        help="Długość łańcucha"
    )
    generate_parser.add_argument(
        "--procs", "-p",
        type=int,
        default=os.cpu_count(),
        help="Liczba procesów"
    )
    generate_parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Plik wynikowy CSV"
    )
    
    # Komenda crack
    crack_parser = subparsers.add_parser('crack', help='Próbuje złamać hash')
    crack_parser.add_argument(
        "--hash", "-H",
        type=str,
        required=True,
        help="Hash do złamania (w formacie hex)"
    )
    crack_parser.add_argument(
        "--table", "-t",
        type=str,
        required=True,
        help="Ścieżka do pliku z tablicą tęczową"
    )
    crack_parser.add_argument(
        "--length", "-l",
        type=int,
        required=True,
        help="Długość hasła (musi być taka sama jak przy generowaniu tablicy)"
    )
    crack_parser.add_argument(
        "--chain-length", "-c",
        type=int,
        required=True,
        help="Długość łańcucha (musi być taka sama jak przy generowaniu tablicy)"
    )
    
    return parser.parse_args()

def hash_command(args):
    """Obsługa komendy hash"""
    try:
        if len(args.password) != args.length:
            logger.error(f"Hasło musi mieć dokładnie {args.length} znaków")
            sys.exit(1)
            
        hash_bytes = des_hash(args.password)
        print(f"Hash: {hash_bytes.hex()}")
        print("\nUżyj tego hasha z komendą crack:")
        print(f"python scripts/des_tool.py crack --hash {hash_bytes.hex()} --table <twoja_tablica.csv> --length {args.length} --chain-length <długość_łańcucha>")
        
    except Exception as e:
        logger.error(f"Błąd podczas generowania hasha: {e}")
        sys.exit(1)

def generate_command(args):
    """Obsługa komendy generate"""
    try:
        # Generowanie losowych haseł startowych
        logger.info(f"Generowanie {args.chains} losowych haseł o długości {args.length}")
        start_passwords = generate_random_passwords(args.chains, args.length)
        
        # Generowanie tablicy tęczowej
        table = generate_table(
            start_passwords=start_passwords,
            pwd_length=args.length,
            chain_length=args.chain_length,
            num_procs=args.procs,
            batch_size=10000  # Fixed batch size for efficiency
        )
        
        # Zapis do pliku
        output_path = Path(args.output)
        logger.info(f"Zapisuję tablicę tęczową do {output_path}")
        save_table_to_csv(table, output_path, batch_size=10000)
        
        logger.info("✅ Zakończono generowanie tablicy tęczowej")
        logger.info(f"Parametry tablicy:")
        logger.info(f"- Długość hasła: {args.length}")
        logger.info(f"- Długość łańcucha: {args.chain_length}")
        logger.info(f"- Liczba łańcuchów: {args.chains}")
        logger.info(f"\nUżyj tych samych parametrów przy łamaniu hasha!")
        
    except KeyboardInterrupt:
        logger.error("Przerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Wystąpił błąd: {e}")
        sys.exit(1)

def crack_command(args):
    """Obsługa komendy crack"""
    try:
        # Konwertuj hash z hex na bajty
        try:
            target_hash = bytes.fromhex(args.hash)
            if len(target_hash) != 8:
                raise ValueError("Hash musi mieć dokładnie 8 bajtów (16 znaków hex)")
        except ValueError as e:
            logger.error(f"Nieprawidłowy format hasha: {e}")
            sys.exit(1)
        
        # Sprawdź czy plik z tablicą istnieje
        if not os.path.exists(args.table):
            logger.error(f"Plik z tablicą tęczową nie istnieje: {args.table}")
            sys.exit(1)
        
        logger.info(f"Próba złamania hasha: {args.hash}")
        logger.info(f"Używam tablicy tęczowej: {args.table}")
        logger.info(f"Parametry:")
        logger.info(f"- Długość hasła: {args.length}")
        logger.info(f"- Długość łańcucha: {args.chain_length}")
        
        # Próbuj złamać hash
        password = crack_hash(
            target_hash=target_hash,
            rainbow_table_file=args.table,
            pwd_length=args.length,
            chain_length=args.chain_length
        )
        
        if password:
            logger.info(f"✅ Znaleziono hasło: {password}")
            # Weryfikacja
            if des_hash(password) == target_hash:
                logger.info("✅ Weryfikacja hasła pomyślna")
            else:
                logger.error("❌ Błąd weryfikacji hasła!")
        else:
            logger.error("❌ Nie znaleziono hasła")
        
    except KeyboardInterrupt:
        logger.error("Przerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Wystąpił błąd: {e}")
        sys.exit(1)

def main():
    args = parse_args()
    
    if args.command == 'hash':
        hash_command(args)
    elif args.command == 'generate':
        generate_command(args)
    elif args.command == 'crack':
        crack_command(args)
    else:
        logger.error("Nie wybrano komendy. Użyj --help aby zobaczyć dostępne opcje.")
        sys.exit(1)

if __name__ == "__main__":
    main() 