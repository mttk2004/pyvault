"""
PyVault Enhanced Login Window
Modern, animated, and beautiful login experience.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame, QGraphicsOpacityEffect,
    QProgressBar
)
from PySide6.QtCore import (
    Signal, Slot, Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QSequentialAnimationGroup, QParallelAnimationGroup, QRect
)
from PySide6.QtGui import QFont, QPainter, QColor, QLinearGradient

from .design_system import tokens, Shadows, Transitions
from .theme_manager import theme_manager
from .toast_notification import show_error_toast, show_warning_toast, show_success_toast


class AnimatedLineEdit(QLineEdit):
    """Custom line edit with smooth focus animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_animations()
        
    def _setup_animations(self):
        """Setup focus animations"""
        self.focus_in_animation = QPropertyAnimation(self, b"geometry")
        self.focus_in_animation.setDuration(Transitions.duration_fast)
        self.focus_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.focus_out_animation = QPropertyAnimation(self, b"geometry") 
        self.focus_out_animation.setDuration(Transitions.duration_fast)
        self.focus_out_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def focusInEvent(self, event):
        """Animate on focus in"""
        super().focusInEvent(event)
        # Subtle scale animation could be added here
        
    def focusOutEvent(self, event):
        """Animate on focus out"""  
        super().focusOutEvent(event)


class GradientButton(QPushButton):
    """Custom button with gradient background and hover effects"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.is_primary = True
        self._setup_animations()
        
    def _setup_animations(self):
        """Setup hover animations"""
        self.hover_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.hover_effect)
        
        self.hover_animation = QPropertyAnimation(self.hover_effect, b"opacity")
        self.hover_animation.setDuration(200)
        
    def enterEvent(self, event):
        """Animate on hover"""
        super().enterEvent(event)
        self.hover_animation.setStartValue(1.0)
        self.hover_animation.setEndValue(0.9)
        self.hover_animation.start()
        
    def leaveEvent(self, event):
        """Animate on leave"""
        super().leaveEvent(event)
        self.hover_animation.setStartValue(0.9)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()


class PasswordStrengthBar(QProgressBar):
    """Custom password strength indicator"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(4)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {tokens.colors.surface_secondary};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {tokens.colors.error};
                border-radius: 2px;
            }}
        """)
        
    def set_strength(self, strength: int):
        """Set password strength (0-5)"""
        self.setValue(strength)
        self.setMaximum(5)
        
        # Color based on strength
        if strength <= 2:
            color = tokens.colors.error
        elif strength <= 4:
            color = tokens.colors.warning
        else:
            color = tokens.colors.success
            
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {tokens.colors.surface_secondary};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)


class EnhancedLoginWindow(QWidget):
    """Enhanced login window with modern design and animations"""
    
    unlocked = Signal(str)
    
    def __init__(self, vault_exists: bool, parent=None):
        super().__init__(parent)
        self.vault_exists = vault_exists
        self.setWindowTitle("PyVault - Secure Password Manager")
        self.setFixedSize(480, 640)
        
        # Remove window frame for custom styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Apply theme
        theme_manager.register_widget(self)
        
        self._setup_ui()
        self._setup_animations()
        self._apply_theme()
        
        # Show entrance animation
        QTimer.singleShot(100, self._show_entrance_animation)
        
    def _setup_ui(self):
        """Setup the enhanced UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Main container with modern styling
        self.container = QFrame()
        self.container.setObjectName("loginContainer")
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)
        
        # Header section
        self._setup_header(layout)
        
        # Form section
        self._setup_form(layout)
        
        # Footer section
        self._setup_footer(layout)
        
        self.main_layout.addWidget(self.container)
        
    def _setup_header(self, layout):
        """Setup the header with logo and title"""
        # Close button
        close_container = QHBoxLayout()
        close_container.addStretch()
        
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(32, 32)
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.close)
        close_container.addWidget(self.close_button)
        
        layout.addLayout(close_container)
        layout.addSpacing(20)
        
        # Logo
        self.logo_label = QLabel("🔒")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet(f"font-size: 64px; padding: {tokens.spacing.lg}px;")
        layout.addWidget(self.logo_label)
        
        # Title
        self.title_label = QLabel("PyVault")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)
        
        layout.addSpacing(8)
        
        # Subtitle
        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setObjectName("subtitleLabel")
        layout.addWidget(self.subtitle_label)
        
        layout.addSpacing(40)
        
    def _setup_form(self, layout):
        """Setup the form inputs"""
        # Password section
        pwd_label = QLabel("Master Password")
        pwd_label.setObjectName("fieldLabel")
        layout.addWidget(pwd_label)
        
        layout.addSpacing(8)
        
        self.password_input = AnimatedLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setObjectName("passwordInput")
        self.password_input.returnPressed.connect(self.handle_action)
        self.password_input.textChanged.connect(self._on_password_changed)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(20)
        
        # Confirm password (only in create mode)
        if not self.vault_exists:
            confirm_label = QLabel("Confirm Password")
            confirm_label.setObjectName("fieldLabel")
            layout.addWidget(confirm_label)
            
            layout.addSpacing(8)
            
            self.confirm_password_input = AnimatedLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setPlaceholderText("Confirm your password")
            self.confirm_password_input.setObjectName("passwordInput")
            self.confirm_password_input.returnPressed.connect(self.handle_action)
            self.confirm_password_input.textChanged.connect(self._on_password_changed)
            layout.addWidget(self.confirm_password_input)
            
            layout.addSpacing(12)
            
            # Password strength
            self.strength_bar = PasswordStrengthBar()
            layout.addWidget(self.strength_bar)
            
            layout.addSpacing(8)
            
            self.strength_label = QLabel("")
            self.strength_label.setObjectName("strengthLabel")
            layout.addWidget(self.strength_label)
            
            layout.addSpacing(20)
        
        # Error display
        self.error_frame = QFrame()
        self.error_frame.setObjectName("errorFrame")
        self.error_frame.hide()
        
        error_layout = QVBoxLayout(self.error_frame)
        error_layout.setContentsMargins(16, 12, 16, 12)
        
        self.error_label = QLabel("")
        self.error_label.setWordWrap(True)
        self.error_label.setObjectName("errorLabel")
        error_layout.addWidget(self.error_label)
        
        layout.addWidget(self.error_frame)
        layout.addSpacing(10)
        
    def _setup_footer(self, layout):
        """Setup footer with action button"""
        layout.addStretch()
        
        # Action button
        if self.vault_exists:
            button_text = "Unlock Vault"
            self.subtitle_label.setText("Welcome back! Enter your password to unlock your vault.")
        else:
            button_text = "Create Vault"
            self.subtitle_label.setText("Create a secure vault to protect your passwords.")
        
        self.action_button = GradientButton(button_text)
        self.action_button.setObjectName("primaryButton")
        self.action_button.clicked.connect(self.handle_action)
        layout.addWidget(self.action_button)
        
        layout.addSpacing(16)
        
        # Security note
        security_note = QLabel("🔐 Your data is encrypted locally and never leaves your device")
        security_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_note.setObjectName("securityNote")
        layout.addWidget(security_note)
        
    def _setup_animations(self):
        """Setup window animations"""
        # Entrance animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.entrance_fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.entrance_fade.setDuration(Transitions.duration_slow)
        self.entrance_fade.setStartValue(0.0)
        self.entrance_fade.setEndValue(1.0)
        self.entrance_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Scale animation for container
        self.container_scale = QPropertyAnimation(self.container, b"geometry")
        self.container_scale.setDuration(Transitions.duration_slow)
        self.container_scale.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Combined entrance animation
        self.entrance_group = QParallelAnimationGroup()
        self.entrance_group.addAnimation(self.entrance_fade)
        
    def _apply_theme(self):
        """Apply current theme styling"""
        colors = tokens.colors
        typography = tokens.typography
        
        self.setStyleSheet(f"""
            /* Main container */
            QFrame#loginContainer {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {tokens.border_radius.xl}px;
                box-shadow: {tokens.shadows.xl};
            }}
            
            /* Close button */
            QPushButton#closeButton {{
                background-color: transparent;
                border: 1px solid {colors.border};
                border-radius: 16px;
                color: {colors.text_tertiary};
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton#closeButton:hover {{
                background-color: {colors.error_light};
                border-color: {colors.error};
                color: {colors.error};
            }}
            
            /* Title */
            QLabel#titleLabel {{
                color: {colors.text_primary};
                font-family: {typography.font_family_sans};
                font-size: {typography.heading_lg}px;
                font-weight: {typography.font_bold};
                padding: {tokens.spacing.sm}px 0;
            }}
            
            /* Subtitle */
            QLabel#subtitleLabel {{
                color: {colors.text_secondary};
                font-family: {typography.font_family_sans};
                font-size: {typography.text_base}px;
                line-height: 1.5;
            }}
            
            /* Field labels */
            QLabel#fieldLabel {{
                color: {colors.text_primary};
                font-family: {typography.font_family_sans};
                font-size: {typography.text_sm}px;
                font-weight: {typography.font_medium};
                padding-bottom: 4px;
            }}
            
            /* Password inputs */
            QLineEdit#passwordInput {{
                background-color: {colors.input_background};
                border: 1px solid {colors.input_border};
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.md}px {tokens.spacing.lg}px;
                font-family: {typography.font_family_mono};
                font-size: {typography.text_base}px;
                color: {colors.text_primary};
            }}
            QLineEdit#passwordInput:focus {{
                background-color: {colors.surface};
                border-color: {colors.primary};
                outline: none;
            }}
            QLineEdit#passwordInput::placeholder {{
                color: {colors.text_tertiary};
            }}
            
            /* Primary button */
            QPushButton#primaryButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors.primary_500}, stop:1 {colors.primary_600});
                border: none;
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.lg}px {tokens.spacing.xl}px;
                color: white;
                font-family: {typography.font_family_sans};
                font-size: {typography.text_base}px;
                font-weight: {typography.font_semibold};
                box-shadow: {tokens.shadows.sm};
            }}
            QPushButton#primaryButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {colors.primary_600}, stop:1 {colors.primary_700});
            }}
            QPushButton#primaryButton:pressed {{
                background: {colors.primary_700};
            }}
            
            /* Error frame */
            QFrame#errorFrame {{
                background-color: {colors.error_light};
                border: 1px solid {colors.error_border};
                border-radius: {tokens.border_radius.md}px;
            }}
            
            QLabel#errorLabel {{
                color: {colors.error};
                font-family: {typography.font_family_sans};
                font-size: {typography.text_sm}px;
            }}
            
            /* Strength label */
            QLabel#strengthLabel {{
                color: {colors.text_secondary};
                font-family: {typography.font_family_sans};
                font-size: {typography.text_xs}px;
            }}
            
            /* Security note */
            QLabel#securityNote {{
                color: {colors.text_tertiary};
                font-family: {typography.font_family_sans};
                font-size: {typography.text_xs}px;
                padding: {tokens.spacing.sm}px;
            }}
        """)
        
    def _show_entrance_animation(self):
        """Show entrance animation"""
        # Start container slightly smaller
        current_rect = self.container.geometry()
        smaller_rect = QRect(
            current_rect.x() + 10,
            current_rect.y() + 10, 
            current_rect.width() - 20,
            current_rect.height() - 20
        )
        self.container.setGeometry(smaller_rect)
        
        # Animate to full size
        self.container_scale.setStartValue(smaller_rect)
        self.container_scale.setEndValue(current_rect)
        
        self.entrance_group.start()
        
        # Focus on password input after animation
        QTimer.singleShot(Transitions.duration_slow + 100, self.password_input.setFocus)
        
    def _on_password_changed(self):
        """Handle password changes"""
        self.clear_error()
        
        if not self.vault_exists:
            self._update_password_strength()
            
    def _update_password_strength(self):
        """Update password strength indicator"""
        if not hasattr(self, 'password_input'):
            return
            
        password = self.password_input.text()
        if len(password) == 0:
            self.strength_bar.hide()
            self.strength_label.setText("")
            return
            
        self.strength_bar.show()
        
        strength = 0
        feedback = []
        
        # Length checks
        if len(password) >= 8:
            strength += 1
        else:
            feedback.append("at least 8 characters")
            
        if len(password) >= 12:
            strength += 1
            
        # Character variety checks
        if any(c.isupper() for c in password):
            strength += 1
        else:
            feedback.append("uppercase letters")
            
        if any(c.islower() for c in password):
            strength += 1  
        else:
            feedback.append("lowercase letters")
            
        if any(c.isdigit() for c in password):
            strength += 1
        else:
            feedback.append("numbers")
            
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~`" for c in password):
            strength += 1
        else:
            feedback.append("special characters")
            
        self.strength_bar.set_strength(strength)
        
        # Update label
        if strength <= 2:
            self.strength_label.setText(f"Weak - Add {', '.join(feedback[:2])}")
            self.strength_label.setStyleSheet(f"color: {tokens.colors.error};")
        elif strength <= 4:
            self.strength_label.setText(f"Medium - Consider adding {feedback[0] if feedback else 'more variety'}")
            self.strength_label.setStyleSheet(f"color: {tokens.colors.warning};")
        else:
            self.strength_label.setText("Strong password ✓")
            self.strength_label.setStyleSheet(f"color: {tokens.colors.success};")
            
    @Slot()
    def handle_action(self):
        """Handle the main action (unlock or create)"""
        password = self.password_input.text()
        
        # Validation
        if not password:
            self.show_error("Password cannot be empty")
            return
            
        if self.vault_exists:
            # Unlock mode - emit password for verification
            self.unlocked.emit(password)
        else:
            # Create mode - additional validation
            if not hasattr(self, 'confirm_password_input'):
                self.unlocked.emit(password)
                return
                
            confirm_password = self.confirm_password_input.text()
            
            if password != confirm_password:
                self.show_error("Passwords do not match")
                self.confirm_password_input.setFocus()
                return
                
            if len(password) < 8:
                self.show_error("Password must be at least 8 characters long")
                self.password_input.setFocus()
                return
                
            # Success - emit password
            self.unlocked.emit(password)
            
    def show_error(self, message: str):
        """Show error message with animation"""
        self.error_label.setText(message)
        
        if not self.error_frame.isVisible():
            self.error_frame.show()
            
            # Animate error appearance
            effect = QGraphicsOpacityEffect()
            self.error_frame.setGraphicsEffect(effect)
            
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(Transitions.duration_fast)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.start()
            
        # Auto-clear after delay
        QTimer.singleShot(5000, self.clear_error)
        
    def clear_error(self):
        """Clear error message with animation"""
        if self.error_frame.isVisible():
            effect = self.error_frame.graphicsEffect()
            if effect:
                animation = QPropertyAnimation(effect, b"opacity")
                animation.setDuration(Transitions.duration_fast)
                animation.setStartValue(1.0) 
                animation.setEndValue(0.0)
                animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                animation.finished.connect(self.error_frame.hide)
                animation.start()
            else:
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
                
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
            
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if hasattr(self, 'drag_start_position'):
            delta = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPosition().toPoint()
