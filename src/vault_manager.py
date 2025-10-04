import json
import base64

class VaultError(Exception):
    """Custom exception for vault operations."""
    pass

class VaultNotFoundError(VaultError, FileNotFoundError):
    """Raised when the vault file is not found."""
    pass

class VaultCorruptedError(VaultError):
    """Raised when the vault file is corrupted or has an invalid format."""
    pass

def save_vault(file_path: str, salt: bytes, nonce: bytes, ciphertext: bytes):
    """
    Saves the vault data to a file in JSON format.
    The binary data (salt, nonce, ciphertext) is base64 encoded for safe storage.
    """
    if not all([file_path, salt, nonce, ciphertext]):
        raise ValueError("All parameters must be provided and non-empty.")

    vault_data = {
        "salt": base64.b64encode(salt).decode('utf-8'),
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8')
    }

    try:
        with open(file_path, 'w') as f:
            json.dump(vault_data, f, indent=4)
    except IOError as e:
        raise VaultError(f"Failed to write to vault file: {file_path}") from e

def load_vault(file_path: str) -> tuple[bytes, bytes, bytes]:
    """
    Loads the vault data from a JSON file.
    Decodes the base64 encoded data back into bytes.
    """
    try:
        with open(file_path, 'r') as f:
            vault_data = json.load(f)

        if not all(k in vault_data for k in ["salt", "nonce", "ciphertext"]):
            raise VaultCorruptedError("Vault file is missing required fields.")

        salt = base64.b64decode(vault_data["salt"])
        nonce = base64.b64decode(vault_data["nonce"])
        ciphertext = base64.b64decode(vault_data["ciphertext"])

        return salt, nonce, ciphertext

    except FileNotFoundError:
        raise VaultNotFoundError(f"Vault file not found at: {file_path}")
    except (json.JSONDecodeError, base64.binascii.Error, TypeError) as e:
        raise VaultCorruptedError("Vault file is corrupted or has an invalid format.") from e
    except IOError as e:
        raise VaultError(f"Failed to read from vault file: {file_path}") from e
