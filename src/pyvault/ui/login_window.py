import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont

class LoginWindow(QWidget):
    # Signal emitted when the user successfully unlocks the vault or creates a new one.
    # It passes the master password to the main application logic.
    unlocked = Signal(str)

    def __init__(self, vault_exists: bool):
        super().__init__()
        self.vault_exists = vault_exists
        self.setWindowTitle("PyVault - Secure Password Manager")
        self.setFixedSize(450, 550)
        self.setObjectName("LoginWindow")

        # Simple window without transparency
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Main layout with clean white background
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Container with white background
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
            }
        """)

        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(50, 50, 50, 40)
        self.layout.setSpacing(0)

        self.main_layout.addWidget(self.container)
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the UI elements based on whether a vault exists."""
        # Close button - positioned absolutely at top right
        close_button = QPushButton("Close", self)
        close_button.setGeometry(350, 10, 90, 36)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(134, 134, 139, 0.3);
                border-radius: 18px;
                color: #86868b;
                font-size: 13px;
                font-weight: 500;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background-color: rgba(213, 39, 75, 0.1);
                border-color: rgba(213, 39, 75, 0.3);
                color: #d1274b;
            }
        """)
        close_button.clicked.connect(self.close)
        close_button.raise_()  # Bring to front

        # Logo - minimal icon
        logo_label = QLabel("🔒")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 48px; padding: 10px;")
        self.layout.addWidget(logo_label)

        self.layout.addSpacing(10)

        # Title
        title_label = QLabel("PyVault")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 600;
            color: #1d1d1f;
        """)
        self.layout.addWidget(title_label)

        self.layout.addSpacing(8)

        # Subtitle
        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("""
            color: #86868b;
            font-size: 14px;
        """)
        self.layout.addWidget(self.subtitle_label)

        self.layout.addSpacing(40)

        # Password input
        self.password_label = QLabel("Master Password")
        self.password_label.setStyleSheet("""
            color: #1d1d1f;
            font-size: 13px;
            font-weight: 500;
            padding-bottom: 8px;
        """)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f7;
                border: 1px solid #e5e5e7;
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 14px;
                color: #1d1d1f;
            }
            QLineEdit:focus {
                background-color: white;
                border-color: #007aff;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_action)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        self.layout.addSpacing(20)

        if self.vault_exists:
            self._setup_unlock_mode()
        else:
            self._setup_create_mode()

        # Error label
        self.error_label = QLabel("")
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("""
            color: #d1274b;
            background-color: #ffeef1;
            border-radius: 6px;
            padding: 12px;
            font-size: 13px;
        """)
        self.error_label.hide()
        self.layout.addWidget(self.error_label)

        self.layout.addSpacing(10)

        # Spacer
        self.layout.addStretch()

        # Action button
        self.action_button = QPushButton()
        self.action_button.clicked.connect(self.handle_action)
        self.action_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #007aff;
                border: none;
                border-radius: 8px;
                padding: 14px;
                color: white;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0051d5;
            }
        """)
        self.layout.addWidget(self.action_button)

        # Set button text
        if self.vault_exists:
            self.action_button.setText("Unlock Vault")
        else:
            self.action_button.setText("Create Vault")

    def _setup_unlock_mode(self):
        """UI for unlocking an existing vault."""
        self.subtitle_label.setText("Enter your password to unlock")

    def _setup_create_mode(self):
        """UI for creating a new vault."""
        self.subtitle_label.setText("Create a secure vault for your passwords")

        self.confirm_password_label = QLabel("Confirm Password")
        self.confirm_password_label.setStyleSheet("""
            color: #1d1d1f;
            font-size: 13px;
            font-weight: 500;
            padding-bottom: 8px;
        """)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f7;
                border: 1px solid #e5e5e7;
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 14px;
                color: #1d1d1f;
            }
            QLineEdit:focus {
                background-color: white;
                border-color: #007aff;
            }
        """)
        self.confirm_password_input.returnPressed.connect(self.handle_action)

        self.layout.addWidget(self.confirm_password_label)
        self.layout.addWidget(self.confirm_password_input)

        self.layout.addSpacing(12)

        # Password strength
        self.strength_label = QLabel()
        self.strength_label.setStyleSheet("""
            color: #86868b;
            font-size: 12px;
        """)
        self.layout.addWidget(self.strength_label)
        self.password_input.textChanged.connect(self._update_password_strength)

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

    def _update_password_strength(self, password):
        """Updates the password strength indicator."""
        if len(password) == 0:
            self.strength_label.setText("")
            return

        strength = 0
        if len(password) >= 8:
            strength += 1
        if len(password) >= 12:
            strength += 1
        if any(c.isupper() for c in password):
            strength += 1
        if any(c.islower() for c in password):
            strength += 1
        if any(c.isdigit() for c in password):
            strength += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            strength += 1

        if strength <= 2:
            self.strength_label.setText("Weak")
            self.strength_label.setStyleSheet("color: #d1274b; font-size: 12px;")
        elif strength <= 4:
            self.strength_label.setText("Medium")
            self.strength_label.setStyleSheet("color: #f5a623; font-size: 12px;")
        else:
            self.strength_label.setText("Strong")
            self.strength_label.setStyleSheet("color: #30d158; font-size: 12px;")

    def show_error(self, message: str):
        """Displays an error message in the UI."""
        self.error_label.setText(message)
        self.error_label.show()

    def clear_error(self):
        """Clears the error message."""
        self.error_label.setText("")
        self.error_label.hide()

    def close_on_success(self):
        """Closes the window, typically after a successful operation."""
        self.close()
