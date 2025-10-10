# src/services/vault_service.py
import os
import json
from typing import Optional

from src import config, crypto_logic, vault_manager
from src.models.vault import Vault
from src.models.credential_entry import CredentialEntry

class VaultService:
    def __init__(self):
        self.key: Optional[bytes] = None
        self.vault: Optional[Vault] = None
        self.vault_exists = os.path.exists(config.VAULT_FILE)

    def unlock_or_create(self, password: str) -> tuple[bool, str, Optional[Vault]]:
        if not self.vault_exists:
            return self._create_vault(password)
        else:
            return self._unlock_vault(password)

    def _create_vault(self, password: str) -> tuple[bool, str, Optional[Vault]]:
        try:
            salt = crypto_logic.generate_salt()
            self.key = crypto_logic.derive_key(password.encode(), salt)

            self.vault = Vault() # Create an empty vault

            initial_data = json.dumps(self.vault.to_dict()).encode('utf-8')
            nonce, ciphertext = crypto_logic.encrypt(initial_data, self.key)

            vault_manager.save_vault(config.VAULT_FILE, salt, nonce, ciphertext)
            self.vault_exists = True
            return True, "Vault created successfully.", self.vault
        except Exception as e:
            return False, f"Error creating vault: {e}", None

    def _unlock_vault(self, password: str) -> tuple[bool, str, Optional[Vault]]:
        try:
            salt, nonce, ciphertext = vault_manager.load_vault(config.VAULT_FILE)
            self.key = crypto_logic.derive_key(password.encode(), salt)
            decrypted_data = crypto_logic.decrypt(nonce, ciphertext, self.key)

            if decrypted_data is None:
                return False, "Incorrect password or corrupted data.", None

            vault_data = json.loads(decrypted_data.decode('utf-8'))
            self.vault = Vault.from_dict(vault_data)

            return True, "", self.vault
        except ValueError as e: # Specifically catch decryption/validation errors
            return False, str(e), None
        except Exception as e:
            return False, f"An unexpected error occurred: {e}", None

    def save_data(self, all_data: list, category_manager_state: dict):
        if self.key is None or self.vault is None:
            print("Error: Vault is not unlocked, cannot save data.")
            return

        try:
            self.vault.entries = [CredentialEntry.from_dict(d) for d in all_data]
            self.vault.category_manager.from_dict(category_manager_state)

            salt, _, _ = vault_manager.load_vault(config.VAULT_FILE)

            data_to_save = json.dumps(self.vault.to_dict()).encode('utf-8')
            nonce, ciphertext = crypto_logic.encrypt(data_to_save, self.key)

            vault_manager.save_vault(config.VAULT_FILE, salt, nonce, ciphertext)
            print("Vault updated successfully.")
        except Exception as e:
            print(f"Error saving vault: {e}")

    def lock(self):
        self.key = None
        self.vault = None
        print("Vault locked by service.")
