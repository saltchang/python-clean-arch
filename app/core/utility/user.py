import hashlib
import os

_SALT_LENGTH = 8  # This is in bytes
_SALT_HEX_LENGTH = _SALT_LENGTH * 2  # Length in hexadecimal characters
_ENCODING = 'utf-8'


def _hash(text: str, salt: str) -> str:
    return hashlib.sha256((text + salt).encode(_ENCODING)).hexdigest()


def hash_password(password: str) -> str:
    random_salt = os.urandom(_SALT_LENGTH).hex()
    hashed_password = _hash(password, random_salt)

    return f'{random_salt}{hashed_password}'


def verify_password(password: str, hashed_password: str) -> bool:
    hash_salt = hashed_password[:_SALT_HEX_LENGTH]

    new_hash = _hash(password, hash_salt)

    return f'{hash_salt}{new_hash}' == hashed_password
