import re

# Valid diagnosis codes in format A00.0 - Z99.9
DIAGNOSIS_CODES = [f"{letter}{num:02d}.{sub}" 
                  for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" 
                  for num in range(100) 
                  for sub in range(10)]

def validate_policy_number(policy_number: str) -> bool:
    # Policy number should be a 9-digit number
    return bool(re.match(r'^\d{9}$', policy_number))

def validate_diagnosis_code(diagnosis_code: str) -> bool:
    # Diagnosis code should be in format A00.0 - Z99.9
    return bool(re.match(r'^[A-Z]\d{2}\.\d$', diagnosis_code))
