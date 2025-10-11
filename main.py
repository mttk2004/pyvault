# main.py
import tkinter as tk
import ttkbootstrap as ttk
import sys
import os

# Add src to the Python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src import config
from src.app_controller import ApplicationController
from src.ui.ui_manager import UIManager
from src.ui.theme import setup_theme

def ensure_vault_directory():
    """Ensure the vault config directory exists."""
    if not os.path.exists(config.VAULT_DIR):
        os.makedirs(config.VAULT_DIR, mode=0o700)

class PyVaultApp:
    """
    The main application class for the Tkinter version of PyVault.
    """
    def __init__(self):
        # 1. Initialize the root window with the theme
        self.root = ttk.Window(themename="litera")
        self.root.title(config.APP_NAME)
        self.root.withdraw() # Hide root window initially

        # 2. Ensure vault directory exists
        ensure_vault_directory()

        # 3. Core components
        self.controller = ApplicationController()
        self.ui_manager = UIManager(self.root, self.controller)

        # 4. Auto-lock mechanism
        self.lock_timer_id = None
        self._reset_lock_timer() # Start the first timer
        self.root.bind_all("<KeyPress>", self._activity_detected)
        self.root.bind_all("<ButtonPress>", self._activity_detected)

    def _activity_detected(self, event=None):
        """Resets the auto-lock timer whenever user activity is detected."""
        self._reset_lock_timer()

    def _reset_lock_timer(self):
        """Cancels the existing timer and starts a new one."""
        if self.lock_timer_id:
            self.root.after_cancel(self.lock_timer_id)

        # Only set a timer if the main window is open
        if self.ui_manager and self.ui_manager.main_window:
            timeout_ms = config.LOCK_TIMEOUT_MINUTES * 60 * 1000
            self.lock_timer_id = self.root.after(timeout_ms, self.controller.lock_vault)

    def start(self):
        """Show the initial UI and start the Tkinter main loop."""
        self.ui_manager.show_login()
        self.root.mainloop()

if __name__ == "__main__":
    app = PyVaultApp()
    app.start()
