# src/app_controller.py
from src.services.vault_service import VaultService

class ApplicationController:
    """
    Acts as a bridge between the UI and the service layer.
    Uses callbacks to communicate back to the UI layer.
    """
    def __init__(self):
        self.vault_service = VaultService()
        self.vault_exists = self.vault_service.vault_exists

        # Callbacks to be set by the UI layer
        self.unlock_feedback = None
        self.show_main_window_signal = None
        self.lock_signal = None
        self.on_data_updated = None
        self.on_categories_updated = None

    def handle_unlock(self, password: str):
        """Handles the unlock logic by calling the VaultService."""
        success, message, vault = self.vault_service.unlock_or_create(password)
        if self.unlock_feedback: self.unlock_feedback(success, message)
        if success and vault:
            self.vault_exists = True
            if self.show_main_window_signal:
                self.show_main_window_signal(vault.entries, vault.category_manager)

    # --- Entry Callbacks ---
    def handle_add_entry(self, entry_data: dict):
        self.vault_service.add_entry(entry_data)
        if self.on_data_updated and self.vault_service.vault:
            self.on_data_updated(self.vault_service.vault.entries)

    def handle_edit_entry(self, entry_data: dict):
        self.vault_service.update_entry(entry_data)
        if self.on_data_updated and self.vault_service.vault:
            self.on_data_updated(self.vault_service.vault.entries)

    def handle_delete_entry(self, entry_id: str):
        self.vault_service.delete_entry(entry_id)
        if self.on_data_updated and self.vault_service.vault:
            self.on_data_updated(self.vault_service.vault.entries)

    # --- Category Callbacks ---
    def handle_category_add(self, name: str):
        try:
            self.vault_service.add_category(name)
            if self.on_categories_updated and self.vault_service.vault:
                self.on_categories_updated(self.vault_service.vault.category_manager)
        except ValueError as e:
            # In a real app, this would go to a UI error handler
            print(f"Error adding category: {e}")

    def handle_category_edit(self, cat_id: str, new_name: str):
        try:
            self.vault_service.update_category(cat_id, new_name)
            if self.on_categories_updated and self.vault_service.vault:
                self.on_categories_updated(self.vault_service.vault.category_manager)
        except ValueError as e:
            print(f"Error updating category: {e}")

    def handle_category_delete(self, cat_id: str):
        try:
            self.vault_service.delete_category(cat_id)
            if self.on_data_updated and self.vault_service.vault:
                self.on_data_updated(self.vault_service.vault.entries)
            if self.on_categories_updated and self.vault_service.vault:
                self.on_categories_updated(self.vault_service.vault.category_manager)
        except ValueError as e:
            print(f"Error deleting category: {e}")

    def lock_vault(self):
        """Locks the vault and signals the UI."""
        self.vault_service.lock()
        if self.lock_signal:
            self.lock_signal()
