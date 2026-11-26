import re


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value):
    return value.strip().lower()


def valid_email(value):
    return bool(EMAIL_PATTERN.fullmatch(value))
