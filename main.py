import sys
import os
import json
from PySide6.QtCore import QTimer, QObject, QEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

# UI Imports
from src.ui.design_system import LightTheme
from src.ui.login_screen import LoginScreen
from src.ui.main_window import MainWindow as MainApplicationWindow

# Core Logic Imports
from src import crypto_logic
from src import vault_manager
from src.category_manager import CategoryManager

class ApplicationController(QObject):
    # Lock after 5 minutes of inactivity
    LOCK_TIMEOUT_MS = 5 * 60 * 1000

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(LightTheme.STYLESHEET)

        # Install event filter to detect user activity
        self.app.installEventFilter(self)

        self.login_window = QMainWindow()
        self.login_screen = LoginScreen()
        self.login_screen.login_successful.connect(self.handle_login)

        self.login_window.setCentralWidget(self.login_screen)
        self.login_window.setWindowTitle("PyVault - Login")
        self.login_window.setGeometry(100, 100, 400, 250)

        self.main_window = None
        self.encryption_key = None
        self.vault_path = None
        self.vault_data = {}
        self.salt = None

        # Setup auto-lock timer
        self.lock_timer = QTimer(self)
        self.lock_timer.setInterval(self.LOCK_TIMEOUT_MS)
        self.lock_timer.setSingleShot(True)
        self.lock_timer.timeout.connect(self.lock_vault)

    def run(self):
        self.login_window.show()
        sys.exit(self.app.exec())

    def eventFilter(self, obj, event):
        """Resets the lock timer on user activity."""
        if event.type() in [QEvent.KeyPress, QEvent.MouseMove]:
            if self.main_window and self.main_window.isVisible():
                self.reset_lock_timer()
        return super().eventFilter(obj, event)

    def reset_lock_timer(self):
        """Starts or restarts the auto-lock timer."""
        self.lock_timer.start()

    def handle_login(self, vault_path, password):
        self.vault_path = vault_path

        try:
            if os.path.exists(vault_path):
                salt, nonce, ciphertext = vault_manager.load_vault(vault_path)
                self.salt = salt
                self.encryption_key = crypto_logic.derive_key(password.encode(), salt)
                decrypted_data = crypto_logic.decrypt(nonce, ciphertext, self.encryption_key)
                self.vault_data = json.loads(decrypted_data)
            else:
                salt = crypto_logic.generate_salt()
                self.salt = salt
                self.encryption_key = crypto_logic.derive_key(password.encode(), salt)
                cm = CategoryManager()
                self.vault_data = {
                    "categories": cm.to_dict()["categories"],
                    "entries": []
                }
                data_bytes = json.dumps(self.vault_data).encode('utf-8')
                nonce, ciphertext = crypto_logic.encrypt(data_bytes, self.encryption_key)
                vault_manager.save_vault(vault_path, self.salt, nonce, ciphertext)

            self.show_main_window()

        except (vault_manager.VaultError, ValueError) as e:
            QMessageBox.critical(self.login_window, "Error", f"Failed to open vault: {e}")

    def show_main_window(self):
        self.main_window = MainApplicationWindow(self.vault_data, self.save_vault)
        self.main_window.show()
        self.login_window.close()
        self.reset_lock_timer() # Start the timer when the main window is shown

    def lock_vault(self):
        """Locks the application by closing the main window and showing the login screen."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        # Clear sensitive data from memory
        self.encryption_key = None
        self.vault_data = {}
        self.salt = None

        # Clear password field on login screen and show it
        self.login_screen.password.clear()
        self.login_window.show()
        QMessageBox.information(self.login_window, "Vault Locked", "Your vault has been locked due to inactivity.")

    def save_vault(self):
        if not self.vault_path or not self.encryption_key or not self.salt:
            QMessageBox.warning(self.main_window, "Save Error", "Vault information is missing.")
            return

        try:
            data_bytes = json.dumps(self.vault_data).encode('utf-8')
            nonce, ciphertext = crypto_logic.encrypt(data_bytes, self.encryption_key)
            vault_manager.save_vault(self.vault_path, self.salt, nonce, ciphertext)
            print("Vault saved successfully.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Save Failed", f"Could not save the vault: {e}")

if __name__ == "__main__":
    controller = ApplicationController()
    controller.run()
