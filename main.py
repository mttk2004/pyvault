import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject, QEvent

# Add src to the Python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.ui.login_window_enhanced import EnhancedLoginWindow
from src.ui.main_window import MainWindow
from src.ui.theme_manager import theme_manager
from src.ui.toast_notification import show_success_toast
from src.app_controller import ApplicationController, VAULT_DIR
from src.category_manager import CategoryManager

LOCK_TIMEOUT_MINUTES = 5 # Lock after 5 minutes of inactivity

def ensure_vault_directory():
    """Ensure the vault config directory exists."""
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR, mode=0o700)  # Create with secure permissions

class ActivityMonitor(QObject):
    """Monitors user activity to reset the auto-lock timer."""
    activity = QEvent.registerEventType()

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress]:
            # Post a custom event to avoid direct method calls in the filter
            QApplication.postEvent(self.parent(), QEvent(self.activity))
        return super().eventFilter(obj, event)

class PyVaultApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Set application properties
        self.setApplicationName("PyVault")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("PyVault")

        # Initialize theme and vault directory
        theme_manager.initialize()
        ensure_vault_directory()

        # Core application controller
        self.controller = ApplicationController(self)

        # UI Windows
        self.login_window = EnhancedLoginWindow(self.controller.vault_exists)
        self.main_window = None

        # Connections
        self.login_window.unlocked.connect(self.controller.handle_unlock)
        self.controller.unlock_feedback.connect(self.login_window.show_unlock_feedback)
        self.controller.show_main_window_signal.connect(self.show_main_window)
        self.controller.lock_signal.connect(self.handle_lock_request)

        self.login_window.show()

        # Auto-lock timer
        self.lock_timer = QTimer(self)
        self.lock_timer.setSingleShot(True)
        self.lock_timer.timeout.connect(self.controller.lock_vault)

        # Activity monitor
        self.activity_monitor = ActivityMonitor(self)
        self.installEventFilter(self.activity_monitor)

    def event(self, e):
        """Override event handler to catch custom activity events."""
        if e.type() == ActivityMonitor.activity:
            self.reset_lock_timer()
            return True
        return super().event(e)

    def show_main_window(self, data: list, category_manager: CategoryManager):
        """Creates and shows the main application window."""
        self.login_window.hide() # Use hide instead of close to avoid app exit issues

        self.main_window = MainWindow(category_manager)
        self.main_window.populate_table(data)

        # Connect main window signals to controller slots
        self.main_window.data_changed.connect(lambda: self.controller.handle_data_change(
            self.main_window.get_all_data(),
            self.main_window.category_manager.to_dict()
        ))
        self.main_window.lock_requested.connect(self.controller.lock_vault)
        
        self.main_window.show()
        self.reset_lock_timer()
        
        QTimer.singleShot(1000, lambda: show_success_toast("Welcome back to PyVault!", parent=self.main_window))

    def handle_lock_request(self):
        """Handles the UI changes when a lock is requested by the controller."""
        if self.main_window is None:
            return

        self.main_window.close()
        self.main_window = None

        # Re-initialize and show the login window
        self.login_window = EnhancedLoginWindow(self.controller.vault_exists)
        self.login_window.unlocked.connect(self.controller.handle_unlock)
        self.login_window.show()

        self.lock_timer.stop()
        print("UI has been locked.")

    def reset_lock_timer(self):
        """Resets the inactivity timer."""
        if self.main_window and self.main_window.isVisible():
            self.lock_timer.start(LOCK_TIMEOUT_MINUTES * 60 * 1000)

if __name__ == "__main__":
    app = PyVaultApp(sys.argv)
    sys.exit(app.exec())
