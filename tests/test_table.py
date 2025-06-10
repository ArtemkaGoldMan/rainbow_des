"""Tests for table operations."""

import os
from rainbow import save_table_to_csv, load_table_from_csv

def test_table():
    """Test that table save/load works."""
    table = [("start1", "end1"), ("start2", "end2")]
    table_file = "test_table.csv"
    
    # Save and load
    save_table_to_csv(table, table_file)
    loaded = list(load_table_from_csv(table_file))
    
    # Verify
    assert len(loaded) == len(table)
    assert loaded[0][0] == "start1"
    assert loaded[1][1] == "end2"
    
    # Cleanup
    os.remove(table_file) 