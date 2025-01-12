import re

def is_principal_wallet(address: str) -> bool:
    pattern = r'^([a-z2-7]{5}-){10}[a-z2-7]{3}[a-z2-7]?$'
    return bool(re.match(pattern, address))

def is_account_wallet(address: str) -> bool:
    pattern = r"^0x[a-fA-F0-9]{64}$"
    return bool(re.match(pattern, address))

def is_valid_icp_address(address: str) -> bool:
    '''Validate wallet address'''
    return len(address) != 0
