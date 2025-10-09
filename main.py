import sys
import os
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer, QObject, QEvent, Signal

# Add src to the Python path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import enhanced UI components
from src.ui.login_window_enhanced import EnhancedLoginWindow
from src.ui.main_window import MainWindow
from src.ui.theme_manager import theme_manager
from src.ui.toast_notification import show_success_toast, show_info_toast
from src import crypto_logic
from src import vault_manager
from src.category_manager import CategoryManager

# Follow Linux FHS: config data in ~/.config/pyvault/
VAULT_DIR = os.path.expanduser("~/.config/pyvault")
VAULT_FILE = os.path.join(VAULT_DIR, "vault.dat")
LOCK_TIMEOUT_MINUTES = 5 # Lock after 5 minutes of inactivity

def ensure_vault_directory():
    """Ensure the vault config directory exists."""
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR, mode=0o700)  # Create with secure permissions

class ActivityMonitor(QObject):
    activity = Signal()

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress]:
            self.activity.emit()
        return super().eventFilter(obj, event)

class PyVaultApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Set application properties for modern UI
        self.setApplicationName("PyVault")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("PyVault")

        # Initialize theme manager
        theme_manager.initialize()

        self.key = None
        self.data = []
        self.category_manager = CategoryManager()

        # Ensure vault directory exists
        ensure_vault_directory()
        self.vault_exists = os.path.exists(VAULT_FILE)

        # Use enhanced login window
        self.login_window = EnhancedLoginWindow(self.vault_exists)
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

            # Create initial vault data with categories
            initial_vault_data = {
                "entries": [],
                "categories": self.category_manager.to_dict()
            }
            initial_data = json.dumps(initial_vault_data).encode('utf-8')
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
                    self.login_window.show_unlock_feedback(False, "Incorrect password or corrupted data.")
                    return

                vault_data = json.loads(decrypted_data.decode('utf-8'))
                
                # Handle backward compatibility
                if isinstance(vault_data, list):
                    # Old format: just a list of entries
                    self.data = vault_data
                    # Ensure all entries have categories
                    for entry in self.data:
                        if "category" not in entry:
                            entry["category"] = CategoryManager.UNCATEGORIZED_ID
                elif isinstance(vault_data, dict) and "entries" in vault_data:
                    # New format: dict with entries and categories
                    self.data = vault_data.get("entries", [])
                    
                    # Load categories if available
                    if "categories" in vault_data:
                        self.category_manager.from_dict(vault_data["categories"])
                    
                    # Ensure all entries have valid categories
                    self.data = self.category_manager.cleanup_entry_categories(self.data)
                else:
                    # Invalid format
                    self.data = []
                
                self.show_main_window()

            except Exception as e:
                self.login_window.show_unlock_feedback(False, f"Error: {e}")

    def show_main_window(self):
        try:
            # Create enhanced main window
            self.main_window = MainWindow(self.category_manager)
            self.main_window.populate_table(self.data)
            self.main_window.data_changed.connect(self.handle_data_change)
            self.main_window.lock_requested.connect(self.lock_vault)
            self.main_window.show()
            
            self.reset_lock_timer()
            
            # Show successful unlock feedback AFTER main window is ready
            self.login_window.show_unlock_feedback(True)
            
            # Show welcome toast after main window is shown
            QTimer.singleShot(1000, lambda: show_success_toast("Welcome back to PyVault!", parent=self.main_window))
            
        except Exception as e:
            print(f"Error creating main window: {e}")
            import traceback
            traceback.print_exc()
            self.login_window.show_unlock_feedback(False, f"Error creating main window: {e}")

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

            # Save both entries and categories
            vault_data = {
                "entries": self.main_window.get_all_data(),
                "categories": self.category_manager.to_dict()
            }
            data_to_save = json.dumps(vault_data).encode('utf-8')
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
        self.category_manager = CategoryManager()

        self.main_window.close()
        self.main_window = None

        # Re-initialize and show the enhanced login window
        self.login_window = EnhancedLoginWindow(self.vault_exists)
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
