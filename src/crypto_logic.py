import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

from src import config # Import the centralized config

def derive_key(password: bytes, salt: bytes) -> bytes:
    """
    Derives a key from a password and salt using PBKDF2.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    if not salt or len(salt) != config.SALT_SIZE:
        raise ValueError(f"Salt must be {config.SALT_SIZE} bytes.")

    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=config.KEY_SIZE,
        salt=salt,
        iterations=config.ITERATIONS,
        backend=default_backend()
    )
    derived_key = kdf.derive(password)
    return derived_key

def generate_salt() -> bytes:
    """Generates a new random salt for key derivation."""
    return os.urandom(config.SALT_SIZE)

def encrypt(data: bytes, key: bytes) -> tuple[bytes, bytes]:
    """
    Encrypts data using AES-GCM and returns (nonce, ciphertext).
    """
    if not data:
        raise ValueError("Data to encrypt cannot be empty.")
    if not key or len(key) != config.KEY_SIZE:
        raise ValueError(f"Key must be {config.KEY_SIZE} bytes.")

    aesgcm = AESGCM(key)
    nonce = os.urandom(config.AES_NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce, ciphertext

def decrypt(nonce: bytes, ciphertext: bytes, key: bytes) -> bytes:
    """
    Decrypts data using AES-GCM and verifies its authenticity.
    Returns the original data if successful, otherwise raises an exception.
    """
    if not nonce or len(nonce) != config.AES_NONCE_SIZE:
        raise ValueError(f"Nonce must be {config.AES_NONCE_SIZE} bytes.")
    if not ciphertext:
        raise ValueError("Ciphertext cannot be empty.")
    if not key or len(key) != config.KEY_SIZE:
        raise ValueError(f"Key must be {config.KEY_SIZE} bytes.")

    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError("Decryption failed. Incorrect password or corrupted data.") from e
