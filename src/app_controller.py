import os
import json
from PySide6.QtCore import QObject, Signal

from src import crypto_logic
from src import vault_manager
from src.category_manager import CategoryManager

# This path logic should be centralized. For now, it's here.
VAULT_DIR = os.path.expanduser("~/.config/pyvault")
VAULT_FILE = os.path.join(VAULT_DIR, "vault.dat")

class ApplicationController(QObject):
    """
    Manages the application's state and core logic, acting as a bridge
    between the UI and the data/crypto layers.
    """
    # Signals to communicate with the UI layer
    unlock_feedback = Signal(bool, str)  # success/fail, message
    show_main_window_signal = Signal(list, CategoryManager) # data, categories
    lock_signal = Signal() # Request to lock UI

    def __init__(self, parent=None):
        super().__init__(parent)
        self.key = None
        self.data = []
        self.category_manager = CategoryManager()
        self.vault_exists = os.path.exists(VAULT_FILE)

    def handle_unlock(self, password):
        """Handles the logic for unlocking or creating a vault."""
        if not self.vault_exists:
            # Create a new vault
            salt = crypto_logic.generate_salt()
            self.key = crypto_logic.derive_key(password.encode(), salt)

            # Create initial vault data with categories
            initial_vault_data = {
                "entries": [],
                "categories": self.category_manager.to_dict()
            }
            initial_data = json.dumps(initial_vault_data).encode('utf-8')
            nonce, ciphertext = crypto_logic.encrypt(initial_data, self.key)

            # Save the new vault
            vault_manager.save_vault(VAULT_FILE, salt, nonce, ciphertext)
            self.data = []
            self.vault_exists = True # Vault now exists
            self.unlock_feedback.emit(True, "")
            self.show_main_window_signal.emit(self.data, self.category_manager)

        else:
            # Unlock existing vault
            try:
                salt, nonce, ciphertext = vault_manager.load_vault(VAULT_FILE)
                self.key = crypto_logic.derive_key(password.encode(), salt)
                decrypted_data = crypto_logic.decrypt(nonce, ciphertext, self.key)

                if decrypted_data is None:
                    self.unlock_feedback.emit(False, "Incorrect password or corrupted data.")
                    return

                vault_data = json.loads(decrypted_data.decode('utf-8'))

                # Handle backward compatibility and data loading
                if isinstance(vault_data, list):
                    self.data = vault_data
                    for entry in self.data:
                        if "category" not in entry:
                            entry["category"] = CategoryManager.UNCATEGORIZED_ID
                elif isinstance(vault_data, dict) and "entries" in vault_data:
                    self.data = vault_data.get("entries", [])
                    if "categories" in vault_data:
                        self.category_manager.from_dict(vault_data["categories"])
                    self.data = self.category_manager.cleanup_entry_categories(self.data)
                else:
                    self.data = []

                self.unlock_feedback.emit(True, "")
                self.show_main_window_signal.emit(self.data, self.category_manager)

            except Exception as e:
                self.unlock_feedback.emit(False, f"Error: {e}")

    def handle_data_change(self, all_data, category_manager_state):
        """Encrypts and saves the current data to the vault file."""
        if self.key is None:
            print("Error: No encryption key available to save data.")
            return

        try:
            salt, _, _ = vault_manager.load_vault(VAULT_FILE)
            self.category_manager.from_dict(category_manager_state) # Update internal state

            vault_data = {
                "entries": all_data,
                "categories": self.category_manager.to_dict()
            }
            data_to_save = json.dumps(vault_data).encode('utf-8')
            nonce, ciphertext = crypto_logic.encrypt(data_to_save, self.key)

            vault_manager.save_vault(VAULT_FILE, salt, nonce, ciphertext)
            print("Vault updated successfully.")
        except Exception as e:
            print(f"Error saving vault: {e}")

    def lock_vault(self):
        """Resets the application state to a locked state."""
        self.key = None
        self.data = []
        self.category_manager = CategoryManager()
        self.lock_signal.emit()
        print("Vault locked by controller.")
