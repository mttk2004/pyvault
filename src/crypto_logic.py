import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

# Constants
SALT_SIZE = 16
KEY_SIZE = 32  # AES-256
ITERATIONS = 480000  # Recommended by OWASP as of 2021
AES_NONCE_SIZE = 12 # 96 bits is recommended for AES-GCM

def derive_key(password: bytes, salt: bytes) -> bytes:
    """
    Derives a key from a password and salt using PBKDF2.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    if not salt or len(salt) != SALT_SIZE:
        raise ValueError(f"Salt must be {SALT_SIZE} bytes.")

    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    # The password must be bytes. The verification is for development,
    # to ensure the key derivation is consistent.
    derived_key = kdf.derive(password)
    return derived_key

def generate_salt() -> bytes:
    """Generates a new random salt for key derivation."""
    return os.urandom(16)

def encrypt(data: bytes, key: bytes) -> tuple[bytes, bytes]:
    """
    Encrypts data using AES-GCM and returns (nonce, ciphertext).
    """
    if not data:
        raise ValueError("Data to encrypt cannot be empty.")
    if not key or len(key) != KEY_SIZE:
        raise ValueError(f"Key must be {KEY_SIZE} bytes.")

    aesgcm = AESGCM(key)
    nonce = os.urandom(AES_NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, data, None) # No associated data
    return nonce, ciphertext

def decrypt(nonce: bytes, ciphertext: bytes, key: bytes) -> bytes:
    """
    Decrypts data using AES-GCM and verifies its authenticity.
    Returns the original data if successful, otherwise raises an exception.
    """
    if not nonce or len(nonce) != AES_NONCE_SIZE:
        raise ValueError(f"Nonce must be {AES_NONCE_SIZE} bytes.")
    if not ciphertext:
        raise ValueError("Ciphertext cannot be empty.")
    if not key or len(key) != KEY_SIZE:
        raise ValueError(f"Key must be {KEY_SIZE} bytes.")

    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        # In a real app, you might want to log this error, but for the user,
        # it just means decryption failed (wrong password or corrupted data).
        raise ValueError("Decryption failed. Incorrect password or corrupted data.") from e

import hashlib

def hash_key(key: bytes) -> bytes:
    """Hashes the encryption key using SHA256 for verification."""
    if not key or len(key) != KEY_SIZE:
        raise ValueError(f"Key must be {KEY_SIZE} bytes.")

    hasher = hashlib.sha256()
    hasher.update(key)
    return hasher.digest()
