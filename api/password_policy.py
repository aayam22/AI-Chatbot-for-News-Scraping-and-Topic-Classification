import re


MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128

# A small denylist of well-known passwords that are routinely exposed in breaches.
COMMON_PASSWORDS = {
    "000000",
    "111111",
    "11111111",
    "112233",
    "121212",
    "123123",
    "123321",
    "123456",
    "1234567",
    "12345678",
    "123456789",
    "1234567890",
    "654321",
    "abc123",
    "admin",
    "admin123",
    "adminadmin",
    "baseball",
    "dragon",
    "football",
    "iloveyou",
    "letmein",
    "login",
    "monkey",
    "password",
    "password1",
    "password123",
    "passw0rd",
    "qwerty",
    "qwerty123",
    "qwertyuiop",
    "secret",
    "sunshine",
    "welcome",
}

SEQUENTIAL_PATTERNS = (
    "0123456789",
    "1234567890",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiopasdfghjklzxcvbnm",
)


def _personal_tokens(username: str, email: str) -> set[str]:
    tokens = set()
    for value in (username or "", email or ""):
        for token in re.split(r"[^a-z0-9]+", value.casefold()):
            if len(token) >= 3:
                tokens.add(token)
    return tokens


def validate_password_strength(password: str, username: str = "", email: str = "") -> list[str]:
    errors = []
    password = password or ""

    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    if len(password) > MAX_PASSWORD_LENGTH:
        errors.append(f"Password must be at most {MAX_PASSWORD_LENGTH} characters long.")

    if not password.strip():
        errors.append("Password cannot be empty or only spaces.")
        return errors

    lowered = password.casefold()
    compact = re.sub(r"[^a-z0-9]", "", lowered)

    if lowered in COMMON_PASSWORDS or compact in COMMON_PASSWORDS:
        errors.append("Password is too common or has appeared in known breach wordlists.")

    for token in _personal_tokens(username, email):
        if token in compact:
            errors.append("Password must not contain your username or email.")
            break

    if re.fullmatch(r"(.)\1{7,}", password):
        errors.append("Password cannot be a single character repeated many times.")

    if compact and any(compact in pattern for pattern in SEQUENTIAL_PATTERNS):
        errors.append("Password cannot be a simple keyboard or number sequence.")

    has_lower = any(char.islower() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(not char.isalnum() for char in password)

    if sum((has_lower, has_upper, has_digit, has_symbol)) < 3:
        errors.append("Password should use at least three of these: lowercase, uppercase, numbers, symbols.")

    return errors
