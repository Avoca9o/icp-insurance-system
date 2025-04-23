import pytest
from bot.utils.checksum import find_checksum

def test_find_checksum():
    # Test case 1: Basic test
    insurer_scheme = "test_scheme"
    special_conditions = "test_conditions"
    checksum = find_checksum(insurer_scheme, special_conditions)
    assert isinstance(checksum, str)
    assert len(checksum) == 64  # SHA-256 produces 64 character hex string

    # Test case 2: Empty strings
    checksum = find_checksum("", "")
    assert isinstance(checksum, str)
    assert len(checksum) == 64

    # Test case 3: Special characters
    insurer_scheme = "test@scheme#123"
    special_conditions = "test!conditions$456"
    checksum = find_checksum(insurer_scheme, special_conditions)
    assert isinstance(checksum, str)
    assert len(checksum) == 64

    # Test case 4: Different inputs produce different checksums
    checksum1 = find_checksum("scheme1", "conditions1")
    checksum2 = find_checksum("scheme2", "conditions2")
    assert checksum1 != checksum2

    # Test case 5: Same inputs produce same checksum
    checksum1 = find_checksum("scheme", "conditions")
    checksum2 = find_checksum("scheme", "conditions")
    assert checksum1 == checksum2 