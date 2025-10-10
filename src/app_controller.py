# src/app_controller.py
from PySide6.QtCore import QObject, Signal

from src.services.vault_service import VaultService
from src.category_manager import CategoryManager
from src.models.vault import Vault

class ApplicationController(QObject):
    """
    Acts as a bridge between the UI and the service layer.
    It translates UI events into service calls and service results into UI signals.
    """
    unlock_feedback = Signal(bool, str)
    # The signal still sends raw data types to the UI to avoid refactoring the UI yet.
    show_main_window_signal = Signal(list, CategoryManager)
    lock_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vault_service = VaultService()
        self.vault_exists = self.vault_service.vault_exists

    def handle_unlock(self, password: str):
        """
        Handles the unlock logic by calling the VaultService and processing the result.
        """
        success, message, vault = self.vault_service.unlock_or_create(password)

        self.unlock_feedback.emit(success, message)

        if success and vault is not None:
            self.vault_exists = True # Update state after successful creation

            # Convert model objects back to dicts for the UI layer
            ui_data = [entry.to_dict() for entry in vault.entries]

            self.show_main_window_signal.emit(ui_data, vault.category_manager)

    def handle_data_change(self, all_data: list, category_manager_state: dict):
        """
        Passes data change requests from the UI to the VaultService.
        """
        self.vault_service.save_data(all_data, category_manager_state)

    def lock_vault(self):
        """
        Locks the vault via the VaultService and signals the UI to lock.
        """
        self.vault_service.lock()
        self.lock_signal.emit()
        print("Lock signal emitted to UI.")
