#!/usr/bin/env python3
"""
PyVault Enhanced UI Demo
Showcases the modern design system, toast notifications, and enhanced login window.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QComboBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Import enhanced UI components
from ui.design_system import tokens
from ui.theme_manager import theme_manager, Theme
from ui.toast_notification import (
    show_success_toast, show_error_toast, show_warning_toast, show_info_toast,
    ToastType, toast_manager
)
from ui.login_window_enhanced import EnhancedLoginWindow


class DemoMainWindow(QMainWindow):
    """Demo window to showcase enhanced UI features"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVault Enhanced UI Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Apply theme
        theme_manager.register_widget(self)
        self._setup_ui()
        self._apply_theme()
        
        # Connect theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
    def _setup_ui(self):
        """Setup the demo UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header
        header = QLabel("PyVault Enhanced UI Demo")
        header.setObjectName("demoHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_selection_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        layout.addLayout(theme_layout)
        
        # Toast notification demos
        toast_section = QLabel("Toast Notifications")
        toast_section.setObjectName("sectionHeader")
        layout.addWidget(toast_section)
        
        toast_buttons_layout = QHBoxLayout()
        
        success_btn = QPushButton("Show Success")
        success_btn.setObjectName("successButton")
        success_btn.clicked.connect(lambda: show_success_toast("Operation completed successfully!", parent=self))
        toast_buttons_layout.addWidget(success_btn)
        
        error_btn = QPushButton("Show Error")
        error_btn.setObjectName("errorButton") 
        error_btn.clicked.connect(lambda: show_error_toast("Something went wrong! Please try again.", parent=self))
        toast_buttons_layout.addWidget(error_btn)
        
        warning_btn = QPushButton("Show Warning")
        warning_btn.setObjectName("warningButton")
        warning_btn.clicked.connect(lambda: show_warning_toast("Please check your input before proceeding.", parent=self))
        toast_buttons_layout.addWidget(warning_btn)
        
        info_btn = QPushButton("Show Info")
        info_btn.setObjectName("infoButton")
        info_btn.clicked.connect(lambda: show_info_toast("Did you know? PyVault uses AES-256-GCM encryption.", parent=self))
        toast_buttons_layout.addWidget(info_btn)
        
        layout.addLayout(toast_buttons_layout)
        
        # Multiple toasts demo
        multi_toast_btn = QPushButton("Show Multiple Toasts")
        multi_toast_btn.setObjectName("primaryButton")
        multi_toast_btn.clicked.connect(self._show_multiple_toasts)
        layout.addWidget(multi_toast_btn)
        
        # Login window demos
        login_section = QLabel("Login Windows")
        login_section.setObjectName("sectionHeader") 
        layout.addWidget(login_section)
        
        login_buttons_layout = QHBoxLayout()
        
        unlock_login_btn = QPushButton("Show Unlock Login")
        unlock_login_btn.setObjectName("primaryButton")
        unlock_login_btn.clicked.connect(lambda: self._show_login_window(vault_exists=True))
        login_buttons_layout.addWidget(unlock_login_btn)
        
        create_login_btn = QPushButton("Show Create Login")
        create_login_btn.setObjectName("secondaryButton")
        create_login_btn.clicked.connect(lambda: self._show_login_window(vault_exists=False))
        login_buttons_layout.addWidget(create_login_btn)
        
        layout.addLayout(login_buttons_layout)
        
        # Clear toasts
        clear_btn = QPushButton("Clear All Toasts")
        clear_btn.setObjectName("secondaryButton")
        clear_btn.clicked.connect(toast_manager.clear_all_toasts)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        
        # Footer info
        footer = QLabel("🔐 Showcasing modern design system with smooth animations and beautiful notifications")
        footer.setObjectName("footerText")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
    def _apply_theme(self):
        """Apply the current theme styling"""
        colors = tokens.colors
        typography = tokens.typography
        
        self.setStyleSheet(f"""
            /* Main window */
            QMainWindow {{
                background-color: {colors.background};
            }}
            
            /* Headers */
            QLabel#demoHeader {{
                color: {colors.text_primary};
                font-family: {typography.font_family_sans};
                font-size: {typography.heading_xl}px;
                font-weight: {typography.font_bold};
                padding: {tokens.spacing.lg}px 0;
            }}
            
            QLabel#sectionHeader {{
                color: {colors.text_primary};
                font-family: {typography.font_family_sans};
                font-size: {typography.heading_md}px;
                font-weight: {typography.font_semibold};
                padding: {tokens.spacing.md}px 0;
            }}
            
            QLabel#footerText {{
                color: {colors.text_tertiary};
                font-family: {typography.font_family_sans};
                font-size: {typography.text_sm}px;
                padding: {tokens.spacing.md}px;
            }}
            
            /* Buttons */
            QPushButton#primaryButton {{
                background-color: {colors.primary};
                color: white;
                border: none;
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.md}px {tokens.spacing.lg}px;
                font-family: {typography.font_family_sans};
                font-size: {typography.text_base}px;
                font-weight: {typography.font_medium};
                min-width: 120px;
            }}
            QPushButton#primaryButton:hover {{
                background-color: {colors.primary_dark};
            }}
            
            QPushButton#secondaryButton {{
                background-color: {colors.surface_secondary};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.md}px {tokens.spacing.lg}px;
                font-family: {typography.font_family_sans};
                font-size: {typography.text_base}px;
                font-weight: {typography.font_medium};
                min-width: 120px;
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {colors.surface_hover};
            }}
            
            QPushButton#successButton {{
                background-color: {colors.success};
                color: white;
                border: none;
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.sm}px {tokens.spacing.md}px;
                font-family: {typography.font_family_sans};
                font-size: {typography.text_sm}px;
                font-weight: {typography.font_medium};
            }}
            QPushButton#successButton:hover {{
                background-color: {colors.success_dark};
            }}
            
            QPushButton#errorButton {{
                background-color: {colors.error};
                color: white;
                border: none;
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.sm}px {tokens.spacing.md}px;
                font-family: {typography.font_family_sans};
                font-size: {typography.text_sm}px;
                font-weight: {typography.font_medium};
            }}
            QPushButton#errorButton:hover {{
                background-color: {colors.error_dark};
            }}
            
            QPushButton#warningButton {{
                background-color: {colors.warning};
                color: white;
                border: none;
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.sm}px {tokens.spacing.md}px;
                font-family: {typography.font_family_sans};
                font-size: {typography.text_sm}px;
                font-weight: {typography.font_medium};
            }}
            QPushButton#warningButton:hover {{
                background-color: {colors.warning_dark};
            }}
            
            QPushButton#infoButton {{
                background-color: {colors.info};
                color: white;
                border: none;
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.sm}px {tokens.spacing.md}px;
                font-family: {typography.font_family_sans};
                font-size: {typography.text_sm}px;
                font-weight: {typography.font_medium};
            }}
            QPushButton#infoButton:hover {{
                background-color: {colors.info_dark};
            }}
            
            /* Other widgets */
            QComboBox {{
                background-color: {colors.input_background};
                border: 1px solid {colors.input_border};
                border-radius: {tokens.border_radius.sm}px;
                padding: {tokens.spacing.sm}px;
                font-family: {typography.font_family_sans};
                font-size: {typography.text_sm}px;
                color: {colors.text_primary};
                min-width: 100px;
            }}
            QComboBox:focus {{
                border-color: {colors.primary};
            }}
            
            QLabel {{
                color: {colors.text_secondary};
                font-family: {typography.font_family_sans};
                font-size: {typography.text_base}px;
            }}
        """)
    
    def _on_theme_selection_changed(self, theme_name: str):
        """Handle theme selection change"""
        if theme_name == "Dark":
            theme_manager.set_theme(Theme.DARK)
        else:
            theme_manager.set_theme(Theme.LIGHT)
    
    def on_theme_changed(self, theme: Theme):
        """Handle theme changes"""
        self._apply_theme()
        
        # Update combo box without triggering signal
        self.theme_combo.blockSignals(True)
        if theme == Theme.DARK:
            self.theme_combo.setCurrentText("Dark")
        else:
            self.theme_combo.setCurrentText("Light")
        self.theme_combo.blockSignals(False)
    
    def _show_multiple_toasts(self):
        """Show multiple toasts in sequence to demonstrate stacking"""
        show_info_toast("Starting demo sequence...", parent=self)
        
        QTimer.singleShot(500, lambda: show_success_toast("First operation completed", parent=self))
        QTimer.singleShot(1000, lambda: show_warning_toast("Second operation has warnings", parent=self))
        QTimer.singleShot(1500, lambda: show_error_toast("Third operation failed", parent=self))
        QTimer.singleShot(2000, lambda: show_success_toast("Demo sequence finished!", parent=self))
    
    def _show_login_window(self, vault_exists: bool):
        """Show the enhanced login window"""
        login_window = EnhancedLoginWindow(vault_exists=vault_exists, parent=self)
        
        # Handle unlock signal for demo
        def on_unlock_demo(password: str):
            if vault_exists:
                # Simulate unlock validation
                if len(password) >= 4:  # Simple demo validation
                    login_window.show_unlock_feedback(True)
                    show_success_toast(f"Vault unlocked with password: {password}", parent=self)
                else:
                    login_window.show_unlock_feedback(False, "Password too short for demo")
            else:
                # Create mode - always succeed for demo
                login_window.show_unlock_feedback(True)
                show_success_toast(f"New vault created with password: {password}", parent=self)
        
        login_window.unlocked.connect(on_unlock_demo)
        login_window.show()


def main():
    """Run the enhanced UI demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PyVault Enhanced UI Demo")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PyVault")
    
    # Initialize theme manager
    theme_manager.initialize()
    
    # Create and show demo window
    demo = DemoMainWindow()
    demo.show()
    
    # Show welcome toast
    QTimer.singleShot(1000, lambda: show_success_toast(
        "Welcome to PyVault Enhanced UI Demo! 🎉", 
        duration=4000, 
        parent=demo
    ))
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
