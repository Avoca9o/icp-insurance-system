import pytest
from utils.request_validations import check_secondary_filters
from utils.check_sum import checksum
from utils.jwt import create_jwt_token, decode_jwt_token


def test_check_secondary_filters_valid():
    valid_filters = {"key1": 1.0, "key2": 2.0}
    check_secondary_filters(valid_filters)  # Should not raise any exception


def test_check_secondary_filters_invalid_type():
    with pytest.raises(ValueError, match="Secondary filters is not a dictionary"):
        check_secondary_filters("not a dict")


def test_check_secondary_filters_invalid_value_type():
    with pytest.raises(ValueError, match="Secondary filters must be a dictionary of <string>:<float>"):
        check_secondary_filters({"key1": "not a float"})


def test_checksum():
    insurer_scheme = "test_scheme"
    special_conditions = "test_conditions"
    result = checksum(insurer_scheme, special_conditions)
    
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 produces 64 character hex string
    assert result == checksum(insurer_scheme, special_conditions)  # Same input should produce same output


def test_checksum_different_inputs():
    result1 = checksum("scheme1", "conditions1")
    result2 = checksum("scheme2", "conditions2")
    assert result1 != result2  # Different inputs should produce different outputs


def test_create_jwt_token():
    data = {"id": "test_id"}
    token = create_jwt_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_jwt_token():
    data = {"id": "test_id"}
    token = create_jwt_token(data)
    decoded_id = decode_jwt_token(token)
    assert decoded_id == "test_id"


def test_decode_jwt_token_invalid():
    with pytest.raises(Exception):  # jwt.decode will raise an exception for invalid tokens
        decode_jwt_token("invalid_token") 