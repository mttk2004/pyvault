"""
PyVault Login Window - Bitwarden Inspired
Clean, dark-themed login experience.
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Signal, Slot, Qt, QTimer

from .design_system import Colors, get_global_stylesheet
from .toast_notification import show_error_toast, show_success_toast


class EnhancedLoginWindow(QWidget):
    """Bitwarden-inspired login window"""

    unlocked = Signal(str)

    def __init__(self, vault_exists: bool, parent=None):
        super().__init__(parent)
        self.vault_exists = vault_exists

        self.setWindowTitle("PyVault")
        self.setFixedSize(400, 500 if not vault_exists else 450)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Setup the login UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Container frame
        container = QFrame()
        container.setObjectName("container")
        main_layout.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Logo/Icon placeholder
        logo_label = QLabel("🔐")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 48px; margin-bottom: 10px;")
        layout.addWidget(logo_label)

        # Title
        title_label = QLabel("PyVault")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        # Subtitle
        subtitle = "Create your vault" if not self.vault_exists else "Enter your master password"
        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setObjectName("subtitle")
        layout.addWidget(subtitle_label)

        # Form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Master Password")
        self.password_input.returnPressed.connect(self.handle_action)
        form_layout.addWidget(self.password_input)

        # Confirm password (only for new vaults)
        if not self.vault_exists:
            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setPlaceholderText("Confirm Master Password")
            self.confirm_password_input.returnPressed.connect(self.handle_action)
            form_layout.addWidget(self.confirm_password_input)

        layout.addLayout(form_layout)

        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Action button
        button_text = "Unlock Vault" if self.vault_exists else "Create Vault"
        self.action_button = QPushButton(button_text)
        self.action_button.clicked.connect(self.handle_action)
        layout.addWidget(self.action_button)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("secondary")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

    def apply_styles(self):
        """Apply Bitwarden-inspired styles"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.PRIMARY_BG};
                color: {Colors.PRIMARY_TEXT};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            QFrame#container {{
                background-color: {Colors.SECONDARY_BG};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
            
            QLabel#title {{
                font-size: 24px;
                font-weight: 600;
                color: {Colors.PRIMARY_TEXT};
                margin-bottom: 5px;
            }}
            
            QLabel#subtitle {{
                font-size: 14px;
                color: {Colors.SECONDARY_TEXT};
                margin-bottom: 20px;
            }}
            
            QLineEdit {{
                background-color: {Colors.SURFACE_BG};
                color: {Colors.PRIMARY_TEXT};
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                min-height: 20px;
            }}
            
            QLineEdit:focus {{
                border-color: {Colors.BLUE_ACCENT};
            }}
            
            QLineEdit::placeholder {{
                color: {Colors.MUTED_TEXT};
            }}
            
            QPushButton {{
                background-color: {Colors.BLUE_ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: {Colors.BLUE_HOVER};
            }}
            
            QPushButton#secondary {{
                background-color: transparent;
                color: {Colors.SECONDARY_TEXT};
                border: 1px solid {Colors.BORDER};
            }}
            
            QPushButton#secondary:hover {{
                background-color: {Colors.SURFACE_BG};
            }}
        """)

    @Slot()
    def handle_action(self):
        """Handle unlock/create action"""
        password = self.password_input.text()

        if not password:
            show_error_toast("Password cannot be empty", self)
            return

        if self.vault_exists:
            # Unlock existing vault
            self.unlocked.emit(password)
        else:
            # Create new vault
            if not hasattr(self, 'confirm_password_input'):
                self.unlocked.emit(password)
                return
                
            confirm_password = self.confirm_password_input.text()
            if password != confirm_password:
                show_error_toast("Passwords do not match", self)
                return
            if len(password) < 8:
                show_error_toast("Password must be at least 8 characters", self)
                return
            self.unlocked.emit(password)

    def show_unlock_feedback(self, success: bool, message: str = ""):
        """Show feedback for unlock attempts"""
        if success:
            show_success_toast("Vault unlocked successfully!", self)
            QTimer.singleShot(500, self.close)
        else:
            if message:
                show_error_toast(message, self)
            else:
                show_error_toast("Incorrect password. Please try again.", self)

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if hasattr(self, 'drag_start_position') and self.drag_start_position is not None:
            delta = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.drag_start_position = None