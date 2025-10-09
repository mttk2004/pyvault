"""
PyVault Login Window - V2 (Bitwarden Inspired)
A complete rewrite for a clean, dark-themed login experience.
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy, QProgressBar
)
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QPixmap

from .design_system import tokens, get_global_stylesheet
from .toast_notification import show_error_toast

class PasswordStrengthBar(QProgressBar):
    """Custom password strength indicator."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(4)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {tokens.colors.surface_tertiary};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {tokens.colors.error};
                border-radius: 2px;
            }}
        """)

    def set_strength(self, strength: int):
        self.setValue(strength)
        self.setMaximum(5)
        
        if strength <= 2:
            color = tokens.colors.error
        elif strength <= 4:
            color = tokens.colors.warning
        else:
            color = tokens.colors.success
            
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {tokens.colors.surface_tertiary};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)

class EnhancedLoginWindow(QWidget):
    """A Bitwarden-inspired login window with a dark, minimalist design."""
    
    unlocked = Signal(str)
    
    def __init__(self, vault_exists: bool, parent=None):
        super().__init__(parent)
        self.vault_exists = vault_exists
        
        self.setWindowTitle("PyVault")
        self.setFixedSize(380, 520 if not vault_exists else 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self.setStyleSheet(get_global_stylesheet())
        
    def _setup_ui(self):
        """Setup the minimalist UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet(f"""
            QFrame#container {{
                background-color: {tokens.colors.background_secondary};
                border: 1px solid {tokens.colors.border_primary};
                border-radius: {tokens.border_radius.lg}px;
            }}
        """)
        main_layout.addWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(tokens.spacing.xl, tokens.spacing.xl, tokens.spacing.xl, tokens.spacing.xl)
        layout.setSpacing(tokens.spacing.lg)
        
        logo_label = QLabel()
        pixmap = QPixmap("src/assets/icons/lock.svg")
        logo_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        title_label = QLabel("PyVault")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"font-size: {tokens.typography.text_2xl}pt; font-weight: {tokens.typography.font_bold}; color: {tokens.colors.text_primary};")
        layout.addWidget(title_label)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(tokens.spacing.md)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Master Password")
        self.password_input.returnPressed.connect(self.handle_action)
        self.password_input.textChanged.connect(self._on_password_changed)
        form_layout.addWidget(self.password_input)
        
        if not self.vault_exists:
            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setPlaceholderText("Confirm Master Password")
            self.confirm_password_input.returnPressed.connect(self.handle_action)
            form_layout.addWidget(self.confirm_password_input)
            
            self.strength_bar = PasswordStrengthBar()
            form_layout.addWidget(self.strength_bar)
            self.strength_bar.hide()
        
        layout.addLayout(form_layout)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        button_text = "Unlock" if self.vault_exists else "Create Vault"
        self.action_button = QPushButton(button_text)
        self.action_button.setObjectName("PrimaryButton")
        self.action_button.clicked.connect(self.handle_action)
        layout.addWidget(self.action_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

    @Slot()
    def _on_password_changed(self):
        """Handle password changes to update strength bar if needed."""
        if not self.vault_exists:
            self._update_password_strength()

    def _update_password_strength(self):
        """Update password strength indicator visibility and value."""
        password = self.password_input.text()
        if password:
            self.strength_bar.show()
            strength = 0
            if len(password) >= 8: strength += 1
            if any(c.isupper() for c in password): strength += 1
            if any(c.islower() for c in password): strength += 1
            if any(c.isdigit() for c in password): strength += 1
            if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~`" for c in password): strength += 1
            self.strength_bar.set_strength(strength)
        else:
            self.strength_bar.hide()

    @Slot()
    def handle_action(self):
        """Handle the main action (unlock or create)."""
        password = self.password_input.text()
        
        if not password:
            show_error_toast("Password cannot be empty.", parent=self)
            return
            
        if self.vault_exists:
            self.unlocked.emit(password)
        else:
            confirm_password = self.confirm_password_input.text()
            if password != confirm_password:
                show_error_toast("Passwords do not match.", parent=self)
                return
            if len(password) < 8:
                show_error_toast("Password must be at least 8 characters.", parent=self)
                return
            self.unlocked.emit(password)
            
    def show_unlock_feedback(self, success: bool, message: str = ""):
        """Show feedback for unlock attempts."""
        if not success:
            error_message = message or "Incorrect password."
            show_error_toast(error_message, parent=self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_start_position') and self.drag_start_position is not None:
            delta = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_start_position = None
