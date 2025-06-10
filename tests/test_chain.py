"""Tests for chain generation functionality."""

from rainbow import generate_chain

def test_chain():
    """Test that generate_chain works."""
    password = "abc"
    start, end = generate_chain(password, len(password), 5)
    assert start == password
    assert len(end) == len(password) 