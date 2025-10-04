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
        self.setFixedSize(480, 520)
        self.setObjectName("LoginWindow")
        
        # Set window flags for better appearance
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main container with rounded corners
        self.container = QFrame(self)
        self.container.setGeometry(10, 10, 460, 500)
        self.container.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                border-radius: 16px;
            }
        """)

        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(16)

        self._setup_ui()

    def _setup_ui(self):
        """Sets up the UI elements based on whether a vault exists."""
        # Logo/Icon area
        logo_label = QLabel("🔐")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 64px; padding: 20px 0px;")
        self.layout.addWidget(logo_label)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("SubtitleLabel")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.layout.addWidget(self.subtitle_label)

        # Spacer
        self.layout.addSpacing(10)

        # Password input
        self.password_label = QLabel("Master Password")
        self.password_label.setObjectName("PasswordLabel")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your master password")
        self.password_input.returnPressed.connect(self.handle_action)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        if self.vault_exists:
            self._setup_unlock_mode()
        else:
            self._setup_create_mode()

        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()  # Hidden by default
        self.layout.addWidget(self.error_label)

        # Spacer
        self.layout.addStretch()

        # Action button
        self.action_button = QPushButton()
        self.action_button.clicked.connect(self.handle_action)
        self.action_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.layout.addWidget(self.action_button)

        # Set button text after creating it
        if self.vault_exists:
            self.action_button.setText("🔓 Unlock Vault")
        else:
            self.action_button.setText("✨ Create Vault")
            
        # Close button
        close_btn_layout = QHBoxLayout()
        close_btn_layout.addStretch()
        close_button = QPushButton("×")
        close_button.setFixedSize(32, 32)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 16px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        close_button.clicked.connect(self.close)
        close_btn_layout.addWidget(close_button)
        self.layout.insertLayout(0, close_btn_layout)

    def _setup_unlock_mode(self):
        """UI for unlocking an existing vault."""
        self.title_label.setText("Welcome Back!")
        self.subtitle_label.setText("Enter your master password to unlock your vault")

    def _setup_create_mode(self):
        """UI for creating a new vault."""
        self.title_label.setText("Create Your Vault")
        self.subtitle_label.setText("Set a strong master password to protect your credentials")
        
        self.confirm_password_label = QLabel("Confirm Password")
        self.confirm_password_label.setObjectName("PasswordLabel")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Re-enter your password")
        self.confirm_password_input.returnPressed.connect(self.handle_action)
        
        # Insert after password input (at indices 7 and 8)
        self.layout.insertWidget(7, self.confirm_password_label)
        self.layout.insertWidget(8, self.confirm_password_input)
        
        # Add password strength indicator
        self.strength_label = QLabel()
        self.strength_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 12px;")
        self.layout.insertWidget(7, self.strength_label)
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
            self.strength_label.setText("Password strength: ● Weak")
            self.strength_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
        elif strength <= 4:
            self.strength_label.setText("Password strength: ●● Medium")
            self.strength_label.setStyleSheet("color: #ffd93d; font-size: 12px;")
        else:
            self.strength_label.setText("Password strength: ●●● Strong")
            self.strength_label.setStyleSheet("color: #6bcf7f; font-size: 12px;")

    def show_error(self, message: str):
        """Displays an error message in the UI."""
        self.error_label.setText(f"⚠️ {message}")
        self.error_label.show()

    def clear_error(self):
        """Clears the error message."""
        self.error_label.setText("")
        self.error_label.hide()

    def close_on_success(self):
        """Closes the window, typically after a successful operation."""
        self.close()
