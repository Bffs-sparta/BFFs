import re


def email_validator(email):
    EMAIL_REGEX = EMAIL_REGEX = re.compile(
        r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    )
    if not EMAIL_REGEX.match(email):
        return False
    else:
        return True


def nickname_validator(nickname):
    nickname_validation = r"^[가-힣ㄱ-ㅎa-zA-Z0-9._-]{2,8}$"

    if not re.search(nickname_validation, str(nickname)):
        return True
    return False
