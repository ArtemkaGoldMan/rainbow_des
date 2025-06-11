#!/usr/bin/env python3
"""
Benchmark script for rainbow table generation.
Tests different combinations of parameters and saves statistics to CSV files.
Also saves each generated rainbow table for later use in tests.
"""

import os
import sys
import time
import csv
from datetime import datetime
from itertools import product
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rainbow import (
    generate_random_passwords,
    save_table_to_csv,
    load_table_from_csv,
    des_hash
)
from rainbow.table_builder import generate_table 

# Test parameters
PASSWORD_LENGTHS = [6]
CHAIN_LENGTHS = [150]
NUM_CHAINS = [10_000_000]
NUM_PROCESSES = [4, 8]
BATCH_SIZES = [5000]



# Directory for saving tables
TABLES_DIR = "benchmark_tables6"

def get_table_filename(params: Dict) -> str:
    """Generate a unique filename for a rainbow table based on its parameters."""
    return os.path.join(
        TABLES_DIR,
        f"table_p{params['password_length']}_"
        f"c{params['chain_length']}_"
        f"n{params['num_chains']}_"
        f"proc{params['num_processes']}_"
        f"b{params['batch_size']}.csv"
    )

def run_benchmark(
    password_length: int,
    chain_length: int,
    num_chains: int,
    num_processes: int,
    batch_size: int
) -> Dict:
    """Run a single benchmark test with given parameters."""
    
    # Create parameters dict for filename generation
    params = {
        'password_length': password_length,
        'chain_length': chain_length,
        'num_chains': num_chains,
        'num_processes': num_processes,
        'batch_size': batch_size
    }
    
    # Generate test passwords
    passwords, password_gen_time = generate_random_passwords(num_chains, password_length)
    
    # Generate rainbow table using table_builder
    table, table_gen_time = generate_table(
        start_passwords=passwords,
        pwd_length=password_length,
        chain_length=chain_length,
        num_procs=num_processes,
        batch_size=batch_size
    )
    
    # Save table with unique name
    table_file = get_table_filename(params)
    start_time = time.time()
    save_table_to_csv(table, table_file)
    save_time = time.time() - start_time
    
    # Load table back to verify
    start_time = time.time()
    loaded_table = load_table_from_csv(table_file)
    load_time = time.time() - start_time
    
    # Calculate statistics
    unique_chains = len(set((start, end) for start, end in table))
    uniqueness_percentage = (unique_chains / len(table)) * 100
    
    return {
        'password_length': password_length,
        'chain_length': chain_length,
        'num_chains': num_chains,
        'num_processes': num_processes,
        'batch_size': batch_size,
        'total_chains': len(table),
        'unique_chains': unique_chains,
        'uniqueness_percentage': uniqueness_percentage,
        'password_gen_time': password_gen_time,
        'table_gen_time': table_gen_time,
        'save_time': save_time,
        'load_time': load_time,
        'total_time': password_gen_time + table_gen_time + save_time + load_time,
        'table_file': table_file
    }

def save_results(results: List[Dict], filename: str):
    """Save benchmark results to a CSV file."""
    if not results:
        return
        
    fieldnames = results[0].keys()
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

def main():
    """Main function to run all benchmarks."""
    # Create tables directory if it doesn't exist
    os.makedirs(TABLES_DIR, exist_ok=True)
    
    # Calculate total number of combinations
    total_combinations = len(PASSWORD_LENGTHS) * len(CHAIN_LENGTHS) * len(NUM_CHAINS) * len(NUM_PROCESSES) * len(BATCH_SIZES)
    print(f"Starting benchmark with {total_combinations} combinations...")
    print(f"Tables will be saved in: {os.path.abspath(TABLES_DIR)}\n")
    
    # Prepare results list
    results = []
    
    # Run all combinations
    for i, (pwd_len, chain_len, num_chains, num_proc, batch_size) in enumerate(
        product(PASSWORD_LENGTHS, CHAIN_LENGTHS, NUM_CHAINS, NUM_PROCESSES, BATCH_SIZES),
        1
    ):
        print(f"\nRunning test {i}/{total_combinations}")
        print(f"Parameters: pwd_len={pwd_len}, chain_len={chain_len}, num_chains={num_chains}, "
              f"num_proc={num_proc}, batch_size={batch_size}")
        
        try:
            result = run_benchmark(pwd_len, chain_len, num_chains, num_proc, batch_size)
            results.append(result)
            
            # Print progress
            print(f"Test completed: {result['uniqueness_percentage']:.2f}% unique chains, "
                  f"time: {result['total_time']:.2f}s")
            print(f"Table saved to: {result['table_file']}")
            
        except Exception as e:
            print(f"Error in test {i}: {e}")
            continue
    
    # Save results to CSV
    if results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"benchmark_results_{timestamp}.csv"
        
        with open(results_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
        print(f"\nResults saved to: {results_file}")
    else:
        print("\nNo results to save - all tests failed!")

if __name__ == "__main__":
    main() 