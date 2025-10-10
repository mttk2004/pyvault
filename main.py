import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject, QEvent

# Add src to the Python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src import config
from src.ui.theme_manager import theme_manager
from src.app_controller import ApplicationController
from src.ui.ui_manager import UIManager # Import the new UIManager

def ensure_vault_directory():
    """Ensure the vault config directory exists."""
    if not os.path.exists(config.VAULT_DIR):
        os.makedirs(config.VAULT_DIR, mode=0o700)

class ActivityMonitor(QObject):
    """Monitors user activity to reset the auto-lock timer."""
    activity = QEvent.registerEventType()

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress]:
            QApplication.postEvent(self.parent(), QEvent(self.activity))
        return super().eventFilter(obj, event)

class PyVaultApp(QApplication):
    """
    The main application class. Responsible for initializing the application,
    controller, UI manager, and handling application-level events like
    the activity monitor for auto-locking.
    """
    def __init__(self, argv):
        super().__init__(argv)

        # Set application properties
        self.setApplicationName(config.APP_NAME)
        self.setApplicationVersion(config.APP_VERSION)
        self.setOrganizationName(config.ORGANIZATION_NAME)

        # Initialize theme and vault directory
        theme_manager.initialize()
        ensure_vault_directory()

        # Core components
        self.controller = ApplicationController(self)
        self.ui_manager = UIManager(self.controller) # UIManager now handles windows

        # Show the initial UI
        self.ui_manager.show_login()

        # Auto-lock timer
        self.lock_timer = QTimer(self)
        self.lock_timer.setSingleShot(True)
        self.lock_timer.timeout.connect(self.controller.lock_vault)

        # Activity monitor setup
        self.activity_monitor = ActivityMonitor(self)
        self.installEventFilter(self.activity_monitor)

    def event(self, e: QEvent):
        """
        Override event handler to catch custom activity events and reset
        the auto-lock timer.
        """
        if e.type() == ActivityMonitor.activity:
            self.reset_lock_timer()
            return True
        return super().event(e)

    def reset_lock_timer(self):
        """
        Resets the inactivity timer if the main window is currently visible.
        """
        if self.ui_manager.main_window and self.ui_manager.main_window.isVisible():
            self.lock_timer.start(config.LOCK_TIMEOUT_MINUTES * 60 * 1000)

if __name__ == "__main__":
    app = PyVaultApp(sys.argv)
    sys.exit(app.exec())
