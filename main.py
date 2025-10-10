import sys
import os
import json
from pathlib import Path
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
    LOCK_TIMEOUT_MS = 5 * 60 * 1000
    VAULT_DIR = Path.home() / ".pyvault"
    VAULT_FILE_PATH = VAULT_DIR / "vault.dat"

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(LightTheme.STYLESHEET)
        self.app.installEventFilter(self)

        self.login_window = QMainWindow()
        self.login_screen = LoginScreen()
        self.login_screen.login_attempted.connect(self.handle_login)

        self.login_window.setCentralWidget(self.login_screen)
        self.login_window.setWindowTitle("PyVault")
        self.login_window.setGeometry(100, 100, 400, 250)

        self.main_window = None
        self.encryption_key = None
        self.vault_data = {}
        self.salt = None
        self.verification_hash = None

        self.lock_timer = QTimer(self)
        self.lock_timer.setInterval(self.LOCK_TIMEOUT_MS)
        self.lock_timer.setSingleShot(True)
        self.lock_timer.timeout.connect(self.lock_vault)

    def run(self):
        # Set the login screen mode based on whether a vault exists
        if os.path.exists(self.VAULT_FILE_PATH):
            self.login_screen.set_mode('unlock')
        else:
            self.login_screen.set_mode('create')

        self.login_window.show()
        sys.exit(self.app.exec())

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.KeyPress, QEvent.MouseMove]:
            if self.main_window and self.main_window.isVisible():
                self.reset_lock_timer()
        return super().eventFilter(obj, event)

    def reset_lock_timer(self):
        self.lock_timer.start()

    def handle_login(self, password):
        mode = self.login_screen.mode
        try:
            if mode == 'create':
                # --- Create New Vault ---
                self.salt = crypto_logic.generate_salt()
                self.encryption_key = crypto_logic.derive_key(password.encode(), self.salt)
                self.verification_hash = crypto_logic.hash_key(self.encryption_key)

                cm = CategoryManager()
                self.vault_data = {"categories": cm.to_dict()["categories"], "entries": []}

                data_bytes = json.dumps(self.vault_data).encode('utf-8')
                nonce, ciphertext = crypto_logic.encrypt(data_bytes, self.encryption_key)
                vault_manager.save_vault(self.VAULT_FILE_PATH, self.salt, self.verification_hash, nonce, ciphertext)

            elif mode == 'unlock':
                # --- Unlock Existing Vault ---
                self.salt, stored_hash, nonce, ciphertext = vault_manager.load_vault(self.VAULT_FILE_PATH)
                self.encryption_key = crypto_logic.derive_key(password.encode(), self.salt)
                current_hash = crypto_logic.hash_key(self.encryption_key)

                if current_hash != stored_hash:
                    QMessageBox.warning(self.login_window, "Error", "Incorrect Master Password.")
                    return

                self.verification_hash = stored_hash
                decrypted_data = crypto_logic.decrypt(nonce, ciphertext, self.encryption_key)
                self.vault_data = json.loads(decrypted_data)

            self.show_main_window()

        except (vault_manager.VaultError, ValueError) as e:
            QMessageBox.critical(self.login_window, "Error", f"Failed to open vault: {e}")

    def show_main_window(self):
        self.main_window = MainApplicationWindow(self.vault_data, self.save_vault)
        self.main_window.show()
        self.login_window.close()
        self.reset_lock_timer()

    def lock_vault(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.encryption_key = None
        self.vault_data = {}
        self.salt = None
        self.verification_hash = None

        self.login_screen.set_mode('unlock')
        self.login_screen.clear_fields()
        self.login_window.show()
        QMessageBox.information(self.login_window, "Vault Locked", "Your vault has been locked due to inactivity.")

    def save_vault(self):
        if not all([self.VAULT_FILE_PATH, self.encryption_key, self.salt, self.verification_hash]):
            QMessageBox.warning(self.main_window, "Save Error", "Vault information is missing.")
            return

        try:
            data_bytes = json.dumps(self.vault_data).encode('utf-8')
            nonce, ciphertext = crypto_logic.encrypt(data_bytes, self.encryption_key)
            vault_manager.save_vault(
                self.VAULT_FILE_PATH, self.salt, self.verification_hash, nonce, ciphertext
            )
            print("Vault saved successfully.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Save Failed", f"Could not save the vault: {e}")

if __name__ == "__main__":
    controller = ApplicationController()
    controller.run()
