# src/ui/ui_manager.py
from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow
from src.ui.toast import show_success
from src.models.credential_entry import CredentialEntry
from src.category_manager import CategoryManager

class UIManager:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.login_window = None
        self.main_window = None

        # Connect controller callbacks to UIManager methods
        self.controller.show_main_window_signal = self.show_main_window
        self.controller.lock_signal = self.handle_lock_request
        self.controller.unlock_feedback = self.show_unlock_feedback
        self.controller.on_data_updated = self._handle_data_updated
        self.controller.on_categories_updated = self._handle_categories_updated

    def show_login(self):
        self.root.withdraw()
        self.login_window = LoginWindow(
            self.root,
            vault_exists=self.controller.vault_exists,
            on_unlock=self.controller.handle_unlock
        )

    def show_unlock_feedback(self, success: bool, message: str = ""):
        if self.login_window:
            self.login_window.show_unlock_feedback(success, message)

    def show_main_window(self, data: list[CredentialEntry], category_manager: CategoryManager):
        if self.login_window:
            self.login_window.destroy()
            self.login_window = None

        # Pass all necessary callbacks to the MainWindow
        callbacks = {
            "on_lock": self.controller.lock_vault,
            "on_add": self.controller.handle_add_entry,
            "on_edit": self.controller.handle_edit_entry,
            "on_delete": self.controller.handle_delete_entry,
            "on_category_add": self.controller.handle_category_add,
            "on_category_edit": self.controller.handle_category_edit,
            "on_category_delete": self.controller.handle_category_delete,
        }

        self.main_window = MainWindow(self.root, category_manager, **callbacks)
        self.main_window.populate_all_data(data)

        show_success("Welcome back to PyVault!")

    def handle_lock_request(self):
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
        self.show_login()

    def _handle_data_updated(self, updated_entries: list[CredentialEntry]):
        """Callback to refresh the main window's entry list."""
        if self.main_window:
            self.main_window.populate_all_data(updated_entries)

    def _handle_categories_updated(self, updated_category_manager: CategoryManager):
        """Callback to refresh the main window's category list."""
        if self.main_window:
            self.main_window.category_manager = updated_category_manager
            self.main_window.populate_categories()
            # Also refresh entries in case category changes affect them (e.g., deletion)
            self._handle_data_updated(self.controller.vault_service.vault.entries)
