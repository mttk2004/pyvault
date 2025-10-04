import sys
import os
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer, QObject, QEvent, Signal

# Add src to the Python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from pyvault.ui.login_window import LoginWindow
from pyvault.ui.main_window import MainWindow
from pyvault.ui.styles import MAIN_STYLESHEET
from pyvault import crypto_logic
from pyvault import vault_manager

VAULT_FILE = "vault.dat"
LOCK_TIMEOUT_MINUTES = 5 # Lock after 5 minutes of inactivity

class ActivityMonitor(QObject):
    activity = Signal()

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress]:
            self.activity.emit()
        return super().eventFilter(obj, event)

class PyVaultApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Set application-wide font
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Apply stylesheet
        self.setStyleSheet(MAIN_STYLESHEET)

        self.key = None
        self.data = []
        self.vault_exists = os.path.exists(VAULT_FILE)

        self.login_window = LoginWindow(self.vault_exists)
        self.main_window = None # Created after successful login

        self.login_window.unlocked.connect(self.handle_unlock)
        self.login_window.show()

        # Auto-lock timer
        self.lock_timer = QTimer(self)
        self.lock_timer.setSingleShot(True)
        self.lock_timer.timeout.connect(self.lock_vault)

        # Activity monitor
        self.activity_monitor = ActivityMonitor()
        self.installEventFilter(self.activity_monitor)
        self.activity_monitor.activity.connect(self.reset_lock_timer)

    def handle_unlock(self, password):
        if not self.vault_exists:
            # Create a new vault
            salt = crypto_logic.generate_salt()
            self.key = crypto_logic.derive_key(password.encode(), salt)

            # Encrypt empty data
            initial_data = json.dumps([]).encode('utf-8')
            nonce, ciphertext = crypto_logic.encrypt(initial_data, self.key)

            # Save the new vault
            vault_manager.save_vault(VAULT_FILE, salt, nonce, ciphertext)
            self.data = []
            self.show_main_window()

        else:
            # Unlock existing vault
            try:
                salt, nonce, ciphertext = vault_manager.load_vault(VAULT_FILE)
                self.key = crypto_logic.derive_key(password.encode(), salt)
                decrypted_data = crypto_logic.decrypt(nonce, ciphertext, self.key)

                if decrypted_data is None:
                    self.login_window.show_error("Sai mật khẩu hoặc dữ liệu bị hỏng.")
                    return

                self.data = json.loads(decrypted_data.decode('utf-8'))
                self.show_main_window()

            except Exception as e:
                self.login_window.show_error(f"Lỗi không xác định: {e}")

    def show_main_window(self):
        self.login_window.close_on_success()
        self.main_window = MainWindow()
        self.main_window.populate_table(self.data)
        self.main_window.data_changed.connect(self.handle_data_change)
        self.main_window.lock_requested.connect(self.lock_vault)
        self.main_window.show()
        self.reset_lock_timer()

    def handle_data_change(self):
        """Encrypts and saves the current data to the vault file."""
        if self.key is None:
            # This should not happen in a normal flow
            print("Lỗi: Không có khóa mã hóa để lưu dữ liệu.")
            return

        try:
            # We need the original salt to derive the key again if needed,
            # but for saving, we only need the current key.
            salt, _, _ = vault_manager.load_vault(VAULT_FILE)

            data_to_save = json.dumps(self.main_window.get_all_data()).encode('utf-8')
            nonce, ciphertext = crypto_logic.encrypt(data_to_save, self.key)

            vault_manager.save_vault(VAULT_FILE, salt, nonce, ciphertext)
            print("Vault đã được cập nhật thành công.")
        except Exception as e:
            # In a real app, you'd want a more user-friendly error dialog
            print(f"Lỗi khi lưu vault: {e}")

    def lock_vault(self):
        """Locks the vault, closes the main window, and shows the login screen."""
        if self.main_window is None:
            return # Already locked or not yet open

        self.key = None
        self.data = []

        self.main_window.close()
        self.main_window = None

        # Re-initialize and show the login window
        self.login_window = LoginWindow(self.vault_exists)
        self.login_window.unlocked.connect(self.handle_unlock)
        self.login_window.show()

        self.lock_timer.stop()
        print("Vault locked due to inactivity or user request.")

    def reset_lock_timer(self):
        """Resets the inactivity timer."""
        if self.main_window:
            self.lock_timer.start(LOCK_TIMEOUT_MINUTES * 60 * 1000)

if __name__ == "__main__":
    app = PyVaultApp(sys.argv)
    sys.exit(app.exec())
