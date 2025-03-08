import hashlib

def find_checksum(insurer_scheme: str, special_conditions: str) -> str:
    bytes_data = (insurer_scheme + special_conditions).encode('utf-8')
    hash_object = hashlib.sha256(bytes_data)
    checksum = hash_object.hexdigest()

    return checksum
