"""Provides util functions."""

import hashlib


def create_hash(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()
