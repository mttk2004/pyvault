"""
Design System for PyVault UI
Inspired by the Bitwarden dark theme.
"""

from PySide6.QtGui import QColor

class DarkTheme:
    # Primary Colors
    BACKGROUND = "#1c1c1c"
    PRIMARY = "#121212"
    TEXT = "#ffffff"

    # Accent Colors
    ACCENT = "#9b59b6"  # A shade of purple
    ACCENT_HOVER = "#8e44ad"

    # Secondary Colors
    SECONDARY_BACKGROUND = "#2c2c2c"
    SECONDARY_TEXT = "#a0a0a0"

    # Common UI Elements
    BORDER = "#3a3a3a"
    INPUT_BACKGROUND = "#252525"

    # Status Colors
    SUCCESS = "#2ecc71"
    ERROR = "#e74c3c"
    WARNING = "#f39c12"

    # Font styles
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_NORMAL = "14px"
    FONT_SIZE_LARGE = "16px"
    FONT_SIZE_SMALL = "12px"

    STYLESHEET = f"""
        QWidget {{
            font-family: {FONT_FAMILY};
            font-size: {FONT_SIZE_NORMAL};
            color: {TEXT};
            background-color: {BACKGROUND};
        }}

        QMainWindow {{
            background-color: {BACKGROUND};
        }}

        QLabel {{
            color: {TEXT};
        }}

        QLineEdit, QTextEdit {{
            background-color: {INPUT_BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
            padding: 5px;
            color: {TEXT};
        }}

        QLineEdit:focus, QTextEdit:focus {{
            border: 1px solid {ACCENT};
        }}

        QPushButton {{
            background-color: {ACCENT};
            color: {TEXT};
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}

        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}

        QListWidget {{
            background-color: {SECONDARY_BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
        }}
    """
