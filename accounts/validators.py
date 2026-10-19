import re

from django.core.exceptions import ValidationError

# Accepted input formats: 09123456789, +989123456789, 00989123456789.
# [0-9] is used instead of \d so non-ASCII digits are rejected.
IRAN_MOBILE_INPUT_REGEX = re.compile(r"(?:\+98|098|0)(9[0-9]{9})")

# Single canonical format stored in the database: 09123456789.
STORED_PHONE_NUMBER_REGEX = r"^09[0-9]{9}$"

INVALID_PHONE_NUMBER_MESSAGE = "Enter a valid Iranian mobile phone number."


def normalize_phone_number(value):
    """Validate an Iranian mobile number and return it as 09XXXXXXXXX."""
    match = IRAN_MOBILE_INPUT_REGEX.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        raise ValidationError(INVALID_PHONE_NUMBER_MESSAGE, code="invalid_phone_number")
    return "0" + match.group(1)
