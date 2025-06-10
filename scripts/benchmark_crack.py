#!/usr/bin/env python3
"""
Crack benchmark script for rainbow table testing.
Tests cracking performance using a given rainbow table against 100 random passwords.
"""

import os
import sys
import time
import csv
from datetime import datetime
from typing import Dict, List, Tuple
from statistics import mean, stdev
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rainbow import (
    generate_random_passwords,
    load_table_from_csv,
    des_hash,
    crack_hash
)

# Number of test passwords to try cracking
NUM_TEST_PASSWORDS = 50

# Number of times to repeat the test
NUM_REPEATS = 1

def run_single_crack_benchmark(table_file: str, password_length: int, chain_length: int, run_number: int) -> Dict:
    """Run a single crack benchmark test."""
    # Generate test passwords - fixed parameter order: count first, then length
    test_passwords, gen_time = generate_random_passwords(NUM_TEST_PASSWORDS, password_length)
    
    # Track results
    cracked_passwords = 0
    total_crack_time = 0
    cracked_details = []
    failed_details = []
    
    # Try to crack each password
    for password in test_passwords:
        try:
            hash_value = des_hash(password)
            start_time = time.time()
            result = crack_hash(hash_value, table_file, password_length, chain_length)
            crack_time = time.time() - start_time
            
            if result:
                cracked_passwords += 1
                total_crack_time += crack_time
                cracked_details.append({
                    'password': password,
                    'hash': hash_value,
                    'crack_time': crack_time,
                    'found_password': result
                })
            else:
                failed_details.append({
                    'password': password,
                    'hash': hash_value
                })
        except Exception as e:
            print(f"Error cracking password {password}: {str(e)}")
            failed_details.append({
                'password': password,
                'hash': hash_value,
                'error': str(e)
            })
    
    # Calculate statistics
    success_rate = (cracked_passwords / NUM_TEST_PASSWORDS) * 100
    avg_crack_time = total_crack_time / cracked_passwords if cracked_passwords > 0 else 0
    
    return {
        'run_number': run_number,
        'table_file': table_file,
        'password_length': password_length,
        'chain_length': chain_length,
        'test_passwords': NUM_TEST_PASSWORDS,
        'cracked_passwords': cracked_passwords,
        'success_rate': success_rate,
        'password_gen_time': gen_time,
        'total_crack_time': total_crack_time,
        'avg_crack_time': avg_crack_time,
        'cracked_details': cracked_details,
        'failed_details': failed_details
    }

def calculate_statistics(results: List[Dict]) -> Dict:
    """Calculate statistics from multiple runs."""
    stats = {
        'parameter': {
            'table_file': results[0]['table_file'],
            'password_length': results[0]['password_length'],
            'chain_length': results[0]['chain_length'],
            'num_test_passwords': NUM_TEST_PASSWORDS,
            'num_repeats': NUM_REPEATS
        },
        'cracked_passwords': {
            'mean': mean(r['cracked_passwords'] for r in results),
            'stdev': stdev(r['cracked_passwords'] for r in results) if len(results) > 1 else 0
        },
        'success_rate': {
            'mean': mean(r['success_rate'] for r in results),
            'stdev': stdev(r['success_rate'] for r in results) if len(results) > 1 else 0
        },
        'password_gen_time': {
            'mean': mean(r['password_gen_time'] for r in results),
            'stdev': stdev(r['password_gen_time'] for r in results) if len(results) > 1 else 0
        },
        'avg_crack_time': {
            'mean': mean(r['avg_crack_time'] for r in results),
            'stdev': stdev(r['avg_crack_time'] for r in results) if len(results) > 1 else 0
        }
    }
    return stats

def save_results(results: List[Dict], stats: Dict, filename: str):
    """Save both individual run results and statistics to CSV files."""
    # Save individual run results (excluding the lists of cracked/failed passwords)
    results_for_csv = []
    for r in results:
        result_copy = r.copy()
        result_copy.pop('cracked_details', None)
        result_copy.pop('failed_details', None)
        results_for_csv.append(result_copy)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results_for_csv[0].keys())
        writer.writeheader()
        writer.writerows(results_for_csv)
    
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
        for metric in ['cracked_passwords', 'success_rate', 
                      'password_gen_time', 'avg_crack_time']:
            writer.writerow([
                metric,
                f"{stats[metric]['mean']:.6f}",
                f"{stats[metric]['stdev']:.6f}"
            ])
    
    # Save detailed results (including cracked and failed passwords)
    details_filename = filename.replace('.csv', '_details.csv')
    with open(details_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Run Number', 'Cracked Passwords', 'Failed Passwords'])
        for r in results:
            writer.writerow([
                r['run_number'],
                ', '.join([d['password'] for d in r['cracked_details']]),
                ', '.join([d['password'] for d in r['failed_details']])
            ])

def main():
    """Main function to run crack benchmarks."""
    # Declare globals at the start of the function
    global NUM_TEST_PASSWORDS, NUM_REPEATS
    
    parser = argparse.ArgumentParser(description='Benchmark rainbow table cracking performance')
    parser.add_argument('table_file', help='Path to the rainbow table CSV file')
    parser.add_argument('--length', '-l', type=int, required=True,
                      help='Length of passwords to test')
    parser.add_argument('--chain-length', '-c', type=int, required=True,
                      help='Length of chains in the rainbow table')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.table_file):
        print(f"Error: Table file {args.table_file} does not exist")
        sys.exit(1)
    
    print(f"Starting crack benchmark...")
    print(f"Configuration:")
    print(f"- Table file: {args.table_file}")
    print(f"- Password length: {args.length}")
    print(f"- Chain length: {args.chain_length}")
    print(f"- Number of test passwords: {NUM_TEST_PASSWORDS}")
    print(f"- Number of repeats: {NUM_REPEATS}\n")
    
    # Run benchmarks
    results = []
    for i in range(1, NUM_REPEATS + 1):
        print(f"\nRunning test {i}/{NUM_REPEATS}")
        try:
            result = run_single_crack_benchmark(args.table_file, args.length, args.chain_length, i)
            results.append(result)
            
            # Print progress
            print(f"Test completed: {result['success_rate']:.2f}% success rate, "
                  f"avg crack time: {result['avg_crack_time']:.6f}s")
            print(f"Cracked {result['cracked_passwords']}/{NUM_TEST_PASSWORDS} passwords")
            
        except Exception as e:
            print(f"Error in test {i}: {e}")
            continue
    
    if results:
        # Calculate and save statistics
        stats = calculate_statistics(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"benchmark_crack_results_{timestamp}.csv"
        save_results(results, stats, results_file)
        
        print(f"\nResults saved to: {results_file}")
        print(f"Statistics saved to: {results_file.replace('.csv', '_stats.csv')}")
        print(f"Detailed results saved to: {results_file.replace('.csv', '_details.csv')}")
        
        # Print summary
        print("\nSummary:")
        print(f"Average success rate: {stats['success_rate']['mean']:.2f}% ± {stats['success_rate']['stdev']:.2f}%")
        print(f"Average crack time: {stats['avg_crack_time']['mean']:.6f}s ± {stats['avg_crack_time']['stdev']:.6f}s")
    else:
        print("\nNo results to save - all tests failed!")

if __name__ == "__main__":
    main() 