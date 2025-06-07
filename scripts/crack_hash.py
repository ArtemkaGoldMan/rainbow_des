#!/usr/bin/env python3

import argparse
import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rainbow.crack_hash import crack_hash
from rainbow.generator_chain import des_hash

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Łamanie hasha DES przy użyciu tablicy tęczowej.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--hash", "-H",
        type=str,
        required=True,
        help="Hash do złamania (w formacie hex)"
    )
    parser.add_argument(
        "--table", "-t",
        type=str,
        required=True,
        help="Ścieżka do pliku z tablicą tęczową"
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
        help="Długość łańcucha użyta do generowania tablicy"
    )
    
    return parser.parse_args()

def main():
    args = parse_args()
    
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
        
        # Próbuj złamać hash
        password = crack_hash(
            target_hash=target_hash,
            rainbow_table_file=args.table,
            pwd_length=args.length,
            chain_length=args.chain
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

if __name__ == "__main__":
    main()
