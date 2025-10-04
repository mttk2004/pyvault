import sys
import os
from PySide6.QtWidgets import QApplication

# Add src to the Python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from pyvault.ui.login_window import LoginWindow
from pyvault.ui.main_window import MainWindow

VAULT_FILE = "vault.dat"

class PyVaultApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.vault_exists = os.path.exists(VAULT_FILE)

        self.login_window = LoginWindow(self.vault_exists)
        self.main_window = None # Created after successful login

        self.login_window.unlocked.connect(self.handle_unlock)
        self.login_window.show()

    def handle_unlock(self, password):
        """
        This is where the core logic will be integrated in the next step.
        For now, we'll just simulate a successful login to show the main window.
        """
        print(f"Attempting to unlock with password: {password}")

        # --- Integration Point (for Step 5) ---
        # Here you would:
        # 1. If vault_exists:
        #    - Load salt, nonce, ciphertext from VAULT_FILE
        #    - Derive key from password and salt
        #    - Try to decrypt. If successful, show main window. If not, show error.
        # 2. If not vault_exists:
        #    - Create new salt
        #    - Derive key from password and salt
        #    - Create empty data structure (e.g., empty list)
        #    - Encrypt it with the new key
        #    - Save the new vault
        #    - Show main window.
        # -----------------------------------------

        # For now, just close login and show main window
        self.login_window.close_on_success()

        self.main_window = MainWindow()
        # In a real scenario, you would populate the table with decrypted data
        # self.main_window.populate_table(decrypted_data)
        self.main_window.show()


if __name__ == "__main__":
    app = PyVaultApp(sys.argv)
    sys.exit(app.exec())
