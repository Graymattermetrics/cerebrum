import hashlib


def create_hash(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def format_string(s: str) -> str:
    """Format a string to be more readable."""
    return s.replace("_", " ").title()
