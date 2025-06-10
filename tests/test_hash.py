"""Tests for hash generation functionality."""

from rainbow import des_hash

def test_hash():
    """Test that des_hash works."""
    password = "abc"  # Changed to 3 chars
    hash_bytes = des_hash(password)
    assert len(hash_bytes) == 8  # DES block size is 8 bytes 