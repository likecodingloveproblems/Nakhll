import re

def mobile_number_validator(mobile_number):
    if re.findall(r'^09[\d]{9}$', mobile_number):
        return True
    return False