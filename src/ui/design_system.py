"""
Design System for PyVault UI
A clean, light theme.
"""

from PySide6.QtGui import QColor

class LightTheme:
    # Primary Colors
    BACKGROUND = "#f5f5f5"
    PRIMARY = "#ffffff"
    TEXT = "#212529"

    # Accent Colors
    ACCENT = "#007bff"  # A shade of blue
    ACCENT_HOVER = "#0056b3"

    # Secondary Colors
    SECONDARY_BACKGROUND = "#ffffff"
    SECONDARY_TEXT = "#6c757d"

    # Common UI Elements
    BORDER = "#ced4da"
    INPUT_BACKGROUND = "#ffffff"

    # Status Colors
    SUCCESS = "#28a745"
    ERROR = "#dc3545"
    WARNING = "#ffc107"

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
            background-color: transparent;
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
            color: {PRIMARY};
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

        QTextBrowser {{
            background-color: {SECONDARY_BACKGROUND};
            border: 1px solid {BORDER};
            border-radius: 4px;
        }}
    """
