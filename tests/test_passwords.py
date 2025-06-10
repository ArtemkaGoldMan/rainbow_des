"""Tests for password generation functionality."""

from rainbow import generate_random_passwords

def test_passwords():
    """Test that generate_random_passwords works."""
    passwords, _ = generate_random_passwords(5, 3)
    assert len(passwords) == 5
    assert all(len(pwd) == 3 for pwd in passwords) 