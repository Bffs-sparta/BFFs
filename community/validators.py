import re


def can_only_eng_int_underbar_and_hyphen(value):
    pattern = r"^[a-zA-Z][a-zA-Z0-9_-]{4,}$"
    if not re.match(pattern, value):
        return False
    return True
