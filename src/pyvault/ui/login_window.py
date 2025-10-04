import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Signal, Slot

class LoginWindow(QWidget):
    # Signal emitted when the user successfully unlocks the vault or creates a new one.
    # It passes the master password to the main application logic.
    unlocked = Signal(str)

    def __init__(self, vault_exists: bool):
        super().__init__()
        self.vault_exists = vault_exists
        self.setWindowTitle("PyVault")
        self.setFixedSize(400, 250)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._setup_ui()

    def _setup_ui(self):
        """Sets up the UI elements based on whether a vault exists."""
        self.title_label = QLabel()
        self.layout.addWidget(self.title_label)

        self.password_label = QLabel("Master Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        if self.vault_exists:
            self._setup_unlock_mode()
        else:
            self._setup_create_mode()

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red")
        self.layout.addWidget(self.error_label)

        self.action_button = QPushButton()
        self.action_button.clicked.connect(self.handle_action)
        self.layout.addWidget(self.action_button)

        # Set button text after creating it
        if self.vault_exists:
            self.action_button.setText("Unlock")
        else:
            self.action_button.setText("Create Vault")

    def _setup_unlock_mode(self):
        """UI for unlocking an existing vault."""
        self.title_label.setText("<h2>Unlock Your Vault</h2>")

    def _setup_create_mode(self):
        """UI for creating a new vault."""
        self.title_label.setText("<h2>Create a New Vault</h2>")
        self.confirm_password_label = QLabel("Confirm Master Password:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        # Insert at index 3 to place it after the first password field
        self.layout.insertWidget(3, self.confirm_password_label)
        self.layout.insertWidget(4, self.confirm_password_input)

    @Slot()
    def handle_action(self):
        """Handles the button click for both creating and unlocking."""
        password = self.password_input.text()
        if not password:
            self.show_error("Password cannot be empty.")
            return

        if self.vault_exists:
            # In unlock mode, just emit the password for the main logic to verify
            self.unlocked.emit(password)
        else:
            # In create mode, verify passwords match
            confirm_password = self.confirm_password_input.text()
            if password != confirm_password:
                self.show_error("Passwords do not match.")
                return
            if len(password) < 8:
                self.show_error("Password must be at least 8 characters long.")
                return
            # Emit the new password to be used for creating the vault
            self.unlocked.emit(password)

    def show_error(self, message: str):
        """Displays an error message in the UI."""
        self.error_label.setText(message)

    def clear_error(self):
        """Clears the error message."""
        self.error_label.setText("")

    def close_on_success(self):
        """Closes the window, typically after a successful operation."""
        self.close()
