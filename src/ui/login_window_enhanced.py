"""
PyVault Login Window - V2 (Bitwarden Inspired)
A complete rewrite for a clean, dark-themed login experience.
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy, QProgressBar
)
from PySide6.QtCore import (
    Signal, Slot, Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QParallelAnimationGroup, QRect
)
from PySide6.QtGui import QFont, QPainter, QColor, QLinearGradient, QPixmap

from .design_system import tokens
from .theme_manager import theme_manager
from .toast_notification import show_error_toast, show_warning_toast, show_success_toast


class AnimatedLineEdit(QLineEdit):
    """Custom line edit with focus styling and shake animation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)

    def shake(self):
        """Shake the line edit to indicate an error."""
        start_rect = self.geometry()
        self.animation.setStartValue(start_rect)

        anim_group = QSequentialAnimationGroup()
        for i in range(4):
            rect = QRect(start_rect)
            rect.moveLeft(start_rect.left() + (10 if i % 2 == 0 else -10))
            anim = QPropertyAnimation(self, b"geometry")
            anim.setDuration(50)
            anim.setStartValue(self.geometry())
            anim.setEndValue(rect)
            anim_group.addAnimation(anim)

        anim_group.addAnimation(QPropertyAnimation(self, b"geometry"))
        anim_group.setCurrentTime(0)
        anim_group.start()

    def focusInEvent(self, event):
        """Handle focus in with CSS styling"""
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Handle focus out with CSS styling"""
        super().focusOutEvent(event)


class GradientButton(QPushButton):
    """Custom button with gradient background and hover effects"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.is_primary = True
        self.is_hovered = False

    def enterEvent(self, event):
        """Handle hover enter - use CSS styling instead of animations"""
        super().enterEvent(event)
        self.is_hovered = True
        self.style().unpolish(self)
        self.style().polish(self)

    def leaveEvent(self, event):
        """Handle hover leave - use CSS styling instead of animations"""
        super().leaveEvent(event)
        self.is_hovered = False
        self.style().unpolish(self)
        self.style().polish(self)

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
            self.show_error("Password cannot be empty")
            self.password_input.shake()
            return

        if self.vault_exists:
            self.unlocked.emit(password)
        else:
            confirm_password = self.confirm_password_input.text()
            if password != confirm_password:
                self.show_error("Passwords do not match")
                self.confirm_password_input.shake()
                return
            if len(password) < 8:
                self.show_error("Password must be at least 8 characters long")
                self.password_input.shake()
                return
            self.unlocked.emit(password)

    def show_error(self, message: str):
        """Show error message using a toast notification."""
        show_error_toast(message, parent=self)

    def clear_error(self):
        """Clear error message"""
        if self.error_frame.isVisible():
            self.error_frame.hide()

    def on_theme_changed(self):
        """Handle theme changes"""
        self._apply_theme()

    def show_unlock_feedback(self, success: bool, message: str = ""):
        """Show feedback for unlock attempts"""
        if success:
            show_success_toast("Vault unlocked successfully!", parent=self)
            # Close window after short delay
            QTimer.singleShot(800, self.close)
        else:
            if message:
                self.show_error(message)
            else:
                self.show_error("Incorrect password. Please try again.")
            self.password_input.shake()

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

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
