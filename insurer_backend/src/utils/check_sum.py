import hashlib


def checksum(insurer_scheme: str, special_conditions: str) -> str:
    bytes_data = (insurer_scheme + special_conditions).encode('utf-8')
    hash_object = hashlib.sha256(bytes_data)
    check_sum = hash_object.hexdigest()

    return check_sum
