# rainbow_des/scripts/des_tool.py

"""
Command line tool for generating rainbow tables and cracking DES passwords.
"""

import argparse
import sys
import os
from pathlib import Path
import random
import time

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from rainbow.crack_hash import crack_hash, crack_hashes_from_file
from rainbow.generator_chain import des_hash
from rainbow.table_builder import generate_table
from rainbow.utils import generate_random_passwords, save_table_to_csv, validate_password_length
from rainbow.config import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    DES_BLOCK_SIZE,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CHAIN_LENGTH,
    DEFAULT_NUM_CHAINS
)

def resolve_path(path: str) -> str:
    """
    Resolves a path relative to the project root.
    If the path is absolute, returns it as is.
    """
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_ROOT, path)

def parse_args():
    parser = argparse.ArgumentParser(
        description="System for generating rainbow tables and cracking DES passwords.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # hash
    hash_parser = subparsers.add_parser('hash', help='Generate hash from password')
    hash_parser.add_argument("--password", "-p", type=str, required=True, help="Password to hash")
    hash_parser.add_argument("--length", "-l", type=int, default=3, help="Password length (default: 3)")

    # generate
    generate_parser = subparsers.add_parser('generate', help='Generate rainbow table')
    generate_parser.add_argument("--chains", "-n", type=int, required=True, 
                               help=f"Number of chains (default: {DEFAULT_NUM_CHAINS})")
    generate_parser.add_argument("--length", "-l", type=int, required=True, help="Password length")
    generate_parser.add_argument("--chain-length", "-c", type=int, required=True,
                               help=f"Chain length (default: {DEFAULT_CHAIN_LENGTH})")
    generate_parser.add_argument("--procs", "-p", type=int, default=os.cpu_count(), help="Number of processes")
    generate_parser.add_argument("--batch-size", "-b", type=int, default=DEFAULT_BATCH_SIZE, 
                               help=f"Batch size (default: {DEFAULT_BATCH_SIZE})")
    generate_parser.add_argument("--seed", type=int, help="Random number generator seed")
    generate_parser.add_argument("--output", "-o", type=str, required=True, help="Output CSV file")

    # crack
    crack_parser = subparsers.add_parser('crack', help='Attempt to crack hash')
    crack_parser.add_argument("--hash", "-H", type=str, help="Hash to crack (hex)")
    crack_parser.add_argument("--hash-file", "-f", type=str, help="File containing hashes to crack (one per line)")
    crack_parser.add_argument("--table", "-t", type=str, required=True, help="Rainbow table file")
    crack_parser.add_argument("--length", "-l", type=int, required=True, help="Password length")
    crack_parser.add_argument("--chain-length", "-c", type=int, required=True, help="Chain length")

    return parser.parse_args()


def hash_command(args):
    """Handle hash command"""
    try:
        if not validate_password_length(args.password, args.length):
            print(f"Error: Password must be exactly {args.length} characters and contain only lowercase letters and digits")
            sys.exit(1)

        hash_bytes = des_hash(args.password)
        print(f"Hash: {hash_bytes.hex()}")
        print("\nUse this hash with the crack command:")
        print(f"python scripts/des_tool.py crack --hash {hash_bytes.hex()} --table <your_table.csv> --length {args.length} --chain-length <chain_length>")
    except Exception as e:
        print(f"Error while generating hash: {e}")
        sys.exit(1)


def generate_command(args):
    """Handle generate command"""
    try:
        # Parameter validation
        if args.length < MIN_PASSWORD_LENGTH or args.length > MAX_PASSWORD_LENGTH:
            print(f"Error: Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}")
            sys.exit(1)
            
        if args.chains <= 0:
            print("Error: Number of chains must be greater than 0")
            sys.exit(1)
            
        if args.chain_length <= 0:
            print("Error: Chain length must be greater than 0")
            sys.exit(1)
            
        if args.procs <= 0:
            print("Error: Number of processes must be greater than 0")
            sys.exit(1)
            
        if args.batch_size <= 0:
            print("Error: Batch size must be greater than 0")
            sys.exit(1)

        # Resolve output path
        output_path = resolve_path(args.output)

        print("\nStarting rainbow table generation:")
        print(f"- Number of chains: {args.chains}")
        print(f"- Password length: {args.length}")
        print(f"- Chain length: {args.chain_length}")
        print(f"- Number of processes: {args.procs}")
        print(f"- Batch size: {args.batch_size}")
        if args.seed is not None:
            print(f"- Seed: {args.seed}")
        print(f"- Output file: {output_path}")
        print("\nGenerating random passwords...")

        # Generate random passwords
        passwords, pwd_gen_time = generate_random_passwords(
            args.chains,
            args.length,
            args.seed
        )
        print(f"Generated {len(passwords)} passwords in {pwd_gen_time:.6f}s")
        
        # Generate rainbow table
        print("\nGenerating rainbow table...")
        table, table_gen_time = generate_table(
            passwords,
            args.length,
            args.chain_length,
            args.procs,
            args.seed,
            args.batch_size
        )
        print(f"Generated rainbow table in {table_gen_time:.6f}s")
        
        # Calculate uniqueness statistics
        total_chains = len(table)
        unique_chains = len(set(end_pwd for _, end_pwd in table))
        unique_percentage = (unique_chains / total_chains) * 100
        
        # Save to file
        print(f"\nSaving table to file {output_path}...")
        save_time = save_table_to_csv(table, output_path)
        print(f"Saved table in {save_time:.6f}s")
        
        # Display summary
        print("\nSummary:")
        print(f"- Total number of chains: {total_chains}")
        print(f"- Unique chains: {unique_chains}")
        print(f"- Uniqueness percentage: {unique_percentage:.2f}%")
        print(f"- Password length: {args.length}")
        print(f"- Chain length: {args.chain_length}")
        print(f"- Number of processes: {args.procs}")
        print(f"- Batch size: {args.batch_size}")
        print(f"- Password generation time: {pwd_gen_time:.6f}s")
        print(f"- Table generation time: {table_gen_time:.6f}s")
        print(f"- Save time: {save_time:.6f}s")
        print(f"- Total time: {pwd_gen_time + table_gen_time + save_time:.6f}s")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError while generating table: {e}")
        sys.exit(1)


def crack_command(args):
    """Handle crack command"""
    try:
        # Validate parameters
        if args.length < MIN_PASSWORD_LENGTH or args.length > MAX_PASSWORD_LENGTH:
            print(f"Error: Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}")
            sys.exit(1)
            
        if args.chain_length <= 0:
            print("Error: Chain length must be greater than 0")
            sys.exit(1)

        # Check if either hash or hash file is provided
        if not args.hash and not args.hash_file:
            print("Error: Either --hash or --hash-file must be provided")
            sys.exit(1)

        if args.hash and args.hash_file:
            print("Error: Cannot use both --hash and --hash-file")
            sys.exit(1)

        # Resolve paths
        table_path = resolve_path(args.table)
        if args.hash_file:
            hash_file_path = resolve_path(args.hash_file)

        # Validate table file
        if not os.path.exists(table_path):
            print(f"Error: Rainbow table file does not exist: {table_path}")
            sys.exit(1)
        if os.path.getsize(table_path) < 32:
            print("Warning: Table file appears to be very small - it might be incomplete")

        if args.hash:
            # Single hash cracking
            try:
                target_hash = bytes.fromhex(args.hash)
                if len(target_hash) != DES_BLOCK_SIZE:
                    raise ValueError(f"Hash must be exactly {DES_BLOCK_SIZE} bytes ({DES_BLOCK_SIZE * 2} hex characters)")
            except ValueError as e:
                print(f"Error: Invalid hash format: {e}")
                sys.exit(1)

            print(f"Attempting to crack hash: {args.hash}")
            print(f"Using rainbow table: {table_path}")

            password = crack_hash(
                target_hash=target_hash,
                rainbow_table_file=table_path,
                pwd_length=args.length,
                chain_length=args.chain_length
            )

        else:
            # Multiple hashes from file
            try:
                cracked, total = crack_hashes_from_file(
                    hash_file=hash_file_path,
                    rainbow_table_file=table_path,
                    pwd_length=args.length,
                    chain_length=args.chain_length
                )
            except Exception as e:
                print(f"Error while cracking hashes from file: {e}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError while cracking hash: {e}")
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
        print("Error: No command specified")
        sys.exit(1)


if __name__ == '__main__':
    main()
