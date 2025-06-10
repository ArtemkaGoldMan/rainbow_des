#!/usr/bin/env python3
"""
Repeat benchmark script for rainbow table generation.
Runs the same configuration multiple times to get more reliable performance measurements.
"""

import os
import sys
import time
import csv
from datetime import datetime
from typing import Dict, List, Tuple
from statistics import mean, stdev

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rainbow import (
    generate_random_passwords,
    save_table_to_csv,
    load_table_from_csv,
    des_hash
)
from rainbow.table_builder import generate_table

# Test parameters - single configuration to test
PASSWORD_LENGTH = 3
CHAIN_LENGTH = 100
NUM_CHAINS = 10000
NUM_PROCESSES = 2
BATCH_SIZE = 1000

# Number of times to repeat the test
NUM_REPEATS = 5

# Directory for saving tables
TABLES_DIR = "benchmark_tables_repeat"

def get_table_filename(run_number: int) -> str:
    """Generate a unique filename for a rainbow table based on run number."""
    return os.path.join(
        TABLES_DIR,
        f"table_p{PASSWORD_LENGTH}_"
        f"c{CHAIN_LENGTH}_"
        f"n{NUM_CHAINS}_"
        f"proc{NUM_PROCESSES}_"
        f"b{BATCH_SIZE}_"
        f"run{run_number}.csv"
    )

def run_single_benchmark(run_number: int) -> Dict:
    """Run a single benchmark test."""
    
    # Generate test passwords
    passwords, password_gen_time = generate_random_passwords(NUM_CHAINS, PASSWORD_LENGTH)
    
    # Generate rainbow table using table_builder
    table, table_gen_time = generate_table(
        start_passwords=passwords,
        pwd_length=PASSWORD_LENGTH,
        chain_length=CHAIN_LENGTH,
        num_procs=NUM_PROCESSES,
        batch_size=BATCH_SIZE
    )
    
    # Save table with unique name
    table_file = get_table_filename(run_number)
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
        'run_number': run_number,
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

def calculate_statistics(results: List[Dict]) -> Dict:
    """Calculate statistics from multiple runs."""
    stats = {
        'parameter': {
            'password_length': PASSWORD_LENGTH,
            'chain_length': CHAIN_LENGTH,
            'num_chains': NUM_CHAINS,
            'num_processes': NUM_PROCESSES,
            'batch_size': BATCH_SIZE,
            'num_repeats': NUM_REPEATS
        },
        'total_chains': {
            'mean': mean(r['total_chains'] for r in results),
            'stdev': stdev(r['total_chains'] for r in results) if len(results) > 1 else 0
        },
        'unique_chains': {
            'mean': mean(r['unique_chains'] for r in results),
            'stdev': stdev(r['unique_chains'] for r in results) if len(results) > 1 else 0
        },
        'uniqueness_percentage': {
            'mean': mean(r['uniqueness_percentage'] for r in results),
            'stdev': stdev(r['uniqueness_percentage'] for r in results) if len(results) > 1 else 0
        },
        'password_gen_time': {
            'mean': mean(r['password_gen_time'] for r in results),
            'stdev': stdev(r['password_gen_time'] for r in results) if len(results) > 1 else 0
        },
        'table_gen_time': {
            'mean': mean(r['table_gen_time'] for r in results),
            'stdev': stdev(r['table_gen_time'] for r in results) if len(results) > 1 else 0
        },
        'save_time': {
            'mean': mean(r['save_time'] for r in results),
            'stdev': stdev(r['save_time'] for r in results) if len(results) > 1 else 0
        },
        'load_time': {
            'mean': mean(r['load_time'] for r in results),
            'stdev': stdev(r['load_time'] for r in results) if len(results) > 1 else 0
        },
        'total_time': {
            'mean': mean(r['total_time'] for r in results),
            'stdev': stdev(r['total_time'] for r in results) if len(results) > 1 else 0
        }
    }
    return stats

def save_results(results: List[Dict], stats: Dict, filename: str):
    """Save both individual run results and statistics to CSV files."""
    # Save individual run results
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    # Save statistics
    stats_filename = filename.replace('.csv', '_stats.csv')
    with open(stats_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write parameters
        writer.writerow(['Parameter', 'Value'])
        for param, value in stats['parameter'].items():
            writer.writerow([param, value])
        writer.writerow([])  # Empty row for readability
        
        # Write statistics
        writer.writerow(['Metric', 'Mean', 'Standard Deviation'])
        for metric in ['total_chains', 'unique_chains', 'uniqueness_percentage', 
                      'password_gen_time', 'table_gen_time', 'save_time', 
                      'load_time', 'total_time']:
            writer.writerow([
                metric,
                f"{stats[metric]['mean']:.6f}",
                f"{stats[metric]['stdev']:.6f}"
            ])

def main():
    """Main function to run repeated benchmarks."""
    # Create tables directory if it doesn't exist
    os.makedirs(TABLES_DIR, exist_ok=True)
    
    print(f"Starting repeat benchmark with {NUM_REPEATS} runs...")
    print(f"Configuration:")
    print(f"- Password length: {PASSWORD_LENGTH}")
    print(f"- Chain length: {CHAIN_LENGTH}")
    print(f"- Number of chains: {NUM_CHAINS}")
    print(f"- Number of processes: {NUM_PROCESSES}")
    print(f"- Batch size: {BATCH_SIZE}")
    print(f"Tables will be saved in: {os.path.abspath(TABLES_DIR)}\n")
    
    # Run benchmarks
    results = []
    for i in range(1, NUM_REPEATS + 1):
        print(f"\nRunning test {i}/{NUM_REPEATS}")
        try:
            result = run_single_benchmark(i)
            results.append(result)
            
            # Print progress
            print(f"Test completed: {result['uniqueness_percentage']:.2f}% unique chains, "
                  f"time: {result['total_time']:.2f}s")
            print(f"Table saved to: {result['table_file']}")
            
        except Exception as e:
            print(f"Error in test {i}: {e}")
            continue
    
    if results:
        # Calculate and save statistics
        stats = calculate_statistics(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"benchmark_repeat_results_{timestamp}.csv"
        save_results(results, stats, results_file)
        
        print(f"\nResults saved to: {results_file}")
        print(f"Statistics saved to: {results_file.replace('.csv', '_stats.csv')}")
        
        # Print summary
        print("\nSummary:")
        print(f"Average total time: {stats['total_time']['mean']:.2f}s ± {stats['total_time']['stdev']:.2f}s")
        print(f"Average uniqueness: {stats['uniqueness_percentage']['mean']:.2f}% ± {stats['uniqueness_percentage']['stdev']:.2f}%")
    else:
        print("\nNo results to save - all tests failed!")

if __name__ == "__main__":
    main() 