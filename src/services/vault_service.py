# src/services/vault_service.py
import os
import json
from typing import Optional

from src import config, crypto_logic, vault_manager
from src.models.vault import Vault
from src.models.credential_entry import CredentialEntry
from src.category_manager import Category

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
            self.vault = Vault()
            self._save_vault_to_disk(salt)
            self.vault_exists = True
            return True, "Vault created successfully.", self.vault
        except Exception as e:
            return False, f"Error creating vault: {e}", None

    def _unlock_vault(self, password: str) -> tuple[bool, str, Optional[Vault]]:
        try:
            salt, nonce, ciphertext = vault_manager.load_vault(config.VAULT_FILE)
            self.key = crypto_logic.derive_key(password.encode(), salt)
            decrypted_data = crypto_logic.decrypt(nonce, ciphertext, self.key)
            vault_data = json.loads(decrypted_data.decode('utf-8'))
            self.vault = Vault.from_dict(vault_data)
            return True, "", self.vault
        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"An unexpected error occurred: {e}", None

    def _save_vault_to_disk(self, salt: bytes = None):
        if self.key is None or self.vault is None: raise RuntimeError("Vault is not unlocked.")
        if salt is None: salt, _, _ = vault_manager.load_vault(config.VAULT_FILE)
        data_to_save = json.dumps(self.vault.to_dict()).encode('utf-8')
        nonce, ciphertext = crypto_logic.encrypt(data_to_save, self.key)
        vault_manager.save_vault(config.VAULT_FILE, salt, nonce, ciphertext)
        print("Vault updated successfully.")

    # --- Entry Management ---
    def add_entry(self, entry_data: dict) -> CredentialEntry:
        if self.vault is None: raise RuntimeError("Vault is not loaded.")
        new_entry = CredentialEntry.from_dict(entry_data)
        self.vault.entries.append(new_entry)
        self._save_vault_to_disk()
        return new_entry

    def update_entry(self, entry_data: dict) -> Optional[CredentialEntry]:
        if self.vault is None: return None
        entry_id = entry_data.get("entry_id")
        entry = next((e for e in self.vault.entries if e.entry_id == entry_id), None)
        if entry:
            entry.service = entry_data.get("service", entry.service)
            entry.username = entry_data.get("username", entry.username)
            entry.password = entry_data.get("password", entry.password)
            entry.url = entry_data.get("url", entry.url)
            entry.category_id = entry_data.get("category_id", entry.category_id)
            self._save_vault_to_disk()
            return entry
        return None

    def delete_entry(self, entry_id: str) -> bool:
        if self.vault is None: return False
        original_len = len(self.vault.entries)
        self.vault.entries = [e for e in self.vault.entries if e.entry_id != entry_id]
        if len(self.vault.entries) < original_len:
            self._save_vault_to_disk()
            return True
        return False

    # --- Category Management ---
    def add_category(self, name: str) -> Category:
        if self.vault is None: raise RuntimeError("Vault is not loaded.")
        new_cat = self.vault.category_manager.add_category(name)
        self._save_vault_to_disk()
        return new_cat

    def update_category(self, cat_id: str, new_name: str) -> Optional[Category]:
        if self.vault is None: return None
        updated_cat = self.vault.category_manager.update_category(cat_id, new_name)
        if updated_cat:
            self._save_vault_to_disk()
        return updated_cat

    def delete_category(self, cat_id: str):
        if self.vault is None: raise RuntimeError("Vault is not loaded.")
        # Move entries to uncategorized before deleting
        for entry in self.vault.entries:
            if entry.category_id == cat_id:
                entry.category_id = self.vault.category_manager.UNCATEGORIZED_ID
        self.vault.category_manager.delete_category(cat_id)
        self._save_vault_to_disk()

    def lock(self):
        self.key = None
        self.vault = None
        print("Vault locked by service.")
