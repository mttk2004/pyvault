# src/ui/ui_manager.py
from PySide6.QtCore import QObject, QTimer
from src.ui.login_window_enhanced import EnhancedLoginWindow
from src.ui.main_window import MainWindow
from src.ui.toast_notification import show_success_toast
from src.category_manager import CategoryManager
from src.app_controller import ApplicationController

class UIManager(QObject):
    """
    Manages UI windows, transitions, and signal connections between the UI
    and the application controller.
    """
    def __init__(self, controller: ApplicationController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.login_window: EnhancedLoginWindow | None = None
        self.main_window: MainWindow | None = None

        # Connect controller signals to UI manager slots
        self.controller.show_main_window_signal.connect(self.show_main_window)
        self.controller.lock_signal.connect(self.handle_lock_request)

    def show_login(self):
        """Creates and shows the login window."""
        self.login_window = EnhancedLoginWindow(self.controller.vault_exists)
        # Connect UI signals to controller slots
        self.login_window.unlocked.connect(self.controller.handle_unlock)
        self.controller.unlock_feedback.connect(self.login_window.show_unlock_feedback)
        self.login_window.show()

    def show_main_window(self, data: list, category_manager: CategoryManager):
        """Hides the login window and shows the main application window."""
        if self.login_window:
            self.login_window.hide()

        self.main_window = MainWindow(category_manager)
        self.main_window.populate_table(data)

        # Connect main window signals to controller slots
        self.main_window.data_changed.connect(lambda: self.controller.handle_data_change(
            self.main_window.get_all_data(),
            self.main_window.category_manager.to_dict()
        ))
        self.main_window.lock_requested.connect(self.controller.lock_vault)

        self.main_window.show()

        # Notify user of successful login
        QTimer.singleShot(1000, lambda: show_success_toast("Welcome back to PyVault!", parent=self.main_window))

    def handle_lock_request(self):
        """Handles the UI changes when a vault lock is requested."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        # Show a new login window
        self.show_login()
        print("UI has been locked and login window is shown.")
