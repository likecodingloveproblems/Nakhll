import re


def mobile_number_validator(mobile_number):
    """Validator for mobile number in format of 09123456789"""
    if re.findall(r'^09[\d]{9}$', mobile_number):
        return True
    return False
