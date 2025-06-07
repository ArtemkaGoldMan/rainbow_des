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

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        import re
        if len(args.hash) != 16 or not re.fullmatch(r"[0-9a-fA-F]{16}", args.hash):
            raise ValueError("Hash musi składać się z dokładnie 16 znaków hex (0-9, a-f)")

        try:
            target_hash = bytes.fromhex(args.hash)
        except ValueError as e:
            logger.error(f"Nieprawidłowy format hasha: {e}")
            sys.exit(1)

        if not os.path.exists(args.table):
            logger.error(f"Plik z tablicą tęczową nie istnieje: {args.table}")
            sys.exit(1)

        if os.path.getsize(args.table) < 32:
            logger.warning("Plik tablicy wygląda na bardzo mały – możliwe, że jest niekompletny")

        logger.info(f"Próba złamania hasha: {args.hash}")
        logger.info(f"Używam tablicy tęczowej: {args.table}")

        password = crack_hash(
            target_hash=target_hash,
            rainbow_table_file=args.table,
            pwd_length=args.length,
            chain_length=args.chain
        )

        if password:
            logger.info(f"✅ Znaleziono hasło: {password}")
            if des_hash(password) == target_hash:
                logger.info("✅ Weryfikacja hasła pomyślna")
            else:
                logger.error("❌ Błąd weryfikacji hasła!")
        else:
            logger.error("❌ Nie znaleziono hasła")

    except KeyboardInterrupt:
        logger.error("❌ Przerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ Wystąpił błąd krytyczny: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 