"""Tests for hash cracking functionality."""

import os
from rainbow import des_hash, crack_hash, save_table_to_csv, generate_chain

def test_crack():
    """Test that crack_hash works."""
    # Create a simple table with known password
    password = "abc"
    hash_bytes = des_hash(password)
    
    # Generate a proper chain
    chain_length = 1
    start, end = generate_chain(password, len(password), chain_length)
    
    # Create table with the generated chain
    table = [(start, end)]
    
    # Save table to a file
    table_file = "test_table.csv"
    save_table_to_csv(table, table_file)
    
    # Try to crack
    found = crack_hash(hash_bytes, table_file, len(password), chain_length)
    assert found == password
    
    # Cleanup
    os.remove(table_file) 