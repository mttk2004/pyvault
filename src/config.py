# src/config.py
"""
Centralized configuration and constants for the PyVault application.
"""

import os

# --- Application Info ---
APP_NAME = "PyVault"
APP_VERSION = "2.0.0"
ORGANIZATION_NAME = "PyVault"

# --- File Paths ---
# Use a more cross-platform friendly directory like ~/.pyvault
VAULT_DIR = os.path.expanduser("~/.pyvault")
VAULT_FILE = os.path.join(VAULT_DIR, "vault.dat")

# --- Security ---
LOCK_TIMEOUT_MINUTES = 5  # Lock after 5 minutes of inactivity

# --- Cryptography ---
SALT_SIZE = 16
KEY_SIZE = 32  # AES-256
ITERATIONS = 480000  # OWASP recommendation
AES_NONCE_SIZE = 12 # Recommended for AES-GCM
