import re


def can_only_eng_and_int(value):
    pattern = r"^[a-zA-Z][a-zA-Z0-9]{4,}$"
    if not re.match(pattern, value):
        return False
    return True
