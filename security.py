import base64
import secrets
import string

import bcrypt
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PBKDF2_ITERATIONS = 600_000
KDF_SALT_BYTES = 16


def hash_master_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_master_password(password: str, stored_hash: bytes) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), bytes(stored_hash))
    except ValueError:
        return False


def new_kdf_salt() -> bytes:
    return secrets.token_bytes(KDF_SALT_BYTES)


def derive_fernet_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(salt),
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


class VaultCipher:
    def __init__(self, master_password: str, salt: bytes):
        self._fernet = Fernet(derive_fernet_key(master_password, salt))

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")

    def decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode("ascii")).decode("utf-8")
        except (InvalidToken, ValueError):
            return "<decryption failed>"


def generate_password(length: int = 20, use_symbols: bool = True) -> str:
    alphabet = string.ascii_letters + string.digits
    if use_symbols:
        alphabet += "!@#$%^&*-_=+?"
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        has_lower = any(c.islower() for c in pw)
        has_upper = any(c.isupper() for c in pw)
        has_digit = any(c.isdigit() for c in pw)
        has_symbol = (not use_symbols) or any(not c.isalnum() for c in pw)
        if has_lower and has_upper and has_digit and has_symbol:
            return pw
