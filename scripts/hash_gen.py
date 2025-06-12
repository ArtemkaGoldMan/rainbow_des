import os
import sys
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from rainbow.generator_chain import des_hash
from rainbow.utils import generate_random_passwords

import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate N passwords and their DES hashes.")
    parser.add_argument("--count", "-n", type=int, required=True, help="Number of passwords to generate")
    parser.add_argument("--length", "-l", type=int, default=6, help="Password length")
    parser.add_argument("--out-prefix", "-o", type=str, default="output", help="Prefix for output files (without extension)")
    parser.add_argument("--seed", type=int, help="Optional seed")

    args = parser.parse_args()

    passwords, _ = generate_random_passwords(args.count, args.length, args.seed)

    passwords_file = f"{args.out_prefix}_passwords.txt"
    hashes_file = f"{args.out_prefix}_hashes.txt"

    with open(passwords_file, "w") as pw_f, open(hashes_file, "w") as h_f:
        for pwd in passwords:
            h = des_hash(pwd).hex()
            pw_f.write(pwd + "\n")
            h_f.write(h + "\n")

    print(f"Saved {args.count} passwords to: {passwords_file}")
    print(f"Saved corresponding hashes to: {hashes_file}")

if __name__ == "__main__":
    main()
