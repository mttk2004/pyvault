"""
PyVault Design System - V2 (Bitwarden Inspired)
A complete redesign focusing on a clean, high-contrast dark theme.
"""

from dataclasses import dataclass
from enum import Enum


class Theme(Enum):
    """Available application themes."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

# Main theme color palette (Dark Theme)
@dataclass
class ColorPalette:
    """Color palette for the Bitwarden-inspired dark theme."""
    # Backgrounds
    background_primary: str    # App window background
    background_secondary: str  # Side panels, headers
    background_tertiary: str   # Pop-ups, modals

    # Surfaces (UI components)
    surface_primary: str       # Main content areas, list backgrounds
    surface_secondary: str     # Selected items, hover states
    surface_tertiary: str      # Clicked/active states

    # Text
    text_primary: str          # Primary text, titles
    text_secondary: str        # Secondary text, subtitles, descriptions
    text_tertiary: str         # Disabled text, placeholders
    text_on_primary: str       # Text on primary action buttons

    # Borders
    border_primary: str        # Borders for panels and components
    border_secondary: str      # Subtle borders, dividers
    border_focus: str          # Border color for focused inputs

    # Action Colors (Primary - Blue)
    primary: str
    primary_hover: str
    primary_disabled: str

    # Status Colors
    success: str
    warning: str
    error: str
    info: str
    
    # Legacy compatibility (aliases)
    surface: str = None  # Will be set to surface_primary
    border: str = None   # Will be set to border_primary

# V2 Dark Theme Palette
DARK_PALETTE = ColorPalette(
    # Backgrounds
    background_primary="#121212",
    background_secondary="#1c1c1c",
    background_tertiary="#232323",

    # Surfaces
    surface_primary="#1a1a1a",
    surface_secondary="#242424",
    surface_tertiary="#2d2d2d",

    # Text
    text_primary="#ffffff",
    text_secondary="#cccccc",
    text_tertiary="#888888",
    text_on_primary="#ffffff",

    # Borders
    border_primary="#33373a",
    border_secondary="#2a2a2a",
    border_focus="#5899e2",

    # Action Colors
    primary="#3a86ff",
    primary_hover="#4d94ff",
    primary_disabled="#555555",

    # Status Colors
    success="#28a745",
    warning="#ffc107",
    error="#dc3545",
    info="#17a2b8",
    
    # Legacy compatibility
    surface="#1a1a1a",  # Same as surface_primary
    border="#33373a"    # Same as border_primary
)

# Light Theme Palette
LIGHT_PALETTE = ColorPalette(
    # Backgrounds
    background_primary="#ffffff",
    background_secondary="#f8f9fa",
    background_tertiary="#e9ecef",

    # Surfaces
    surface_primary="#ffffff",
    surface_secondary="#f8f9fa",
    surface_tertiary="#e9ecef",

    # Text
    text_primary="#212529",
    text_secondary="#495057",
    text_tertiary="#6c757d",
    text_on_primary="#ffffff",

    # Borders
    border_primary="#ced4da",
    border_secondary="#dee2e6",
    border_focus="#197bff",

    # Action Colors
    primary="#197bff",
    primary_hover="#0062e6",
    primary_disabled="#adb5bd",

    # Status Colors
    success="#28a745",
    warning="#ffc107",
    error="#dc3545",
    info="#17a2b8",
    
    # Legacy compatibility
    surface="#ffffff",   # Same as surface_primary
    border="#ced4da"     # Same as border_primary
)

@dataclass
class Typography:
    """Typography scale."""
    font_family_sans: str = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif"

    # Font sizes (in pt for Qt)
    text_xs: int = 8
    text_sm: int = 9
    text_base: int = 10
    text_lg: int = 12
    text_xl: int = 14
    text_2xl: int = 18

    # Font weights
    font_normal: int = 400
    font_medium: int = 500
    font_semibold: int = 600
    font_bold: int = 700

@dataclass
class Spacing:
    """Spacing system based on a 4px grid."""
    xxs: int = 4
    xs: int = 8
    sm: int = 12
    md: int = 16
    lg: int = 24
    xl: int = 32

@dataclass
class BorderRadius:
    """Border radius values."""
    sm: int = 4
    md: int = 6
    lg: int = 8

class DesignTokens:
    """Central design tokens for the new UI."""

    def __init__(self):
        self.colors = DARK_PALETTE
        self.typography = Typography()
        self.spacing = Spacing()
        self.border_radius = BorderRadius()
        self.shadows = {}  # Placeholder for shadows

    def switch_theme(self, theme: Theme):
        """Switch between themes."""
        if theme == Theme.DARK:
            self.colors = DARK_PALETTE
        elif theme == Theme.LIGHT:
            self.colors = LIGHT_PALETTE
        # System theme would detect system preference (not implemented)

    def get_color(self, color_name: str) -> str:
        """Get color value by name."""
        return getattr(self.colors, color_name, "#ffffff")

# Global design tokens instance
tokens = DesignTokens()

# Stylesheet Fragments Generator
def get_global_stylesheet() -> str:
    """Returns a global stylesheet for the application."""
    return f"""
        QWidget {{
            background-color: {tokens.colors.background_primary};
            color: {tokens.colors.text_secondary};
            font-family: "{tokens.typography.font_family_sans}";
            font-size: {tokens.typography.text_base}pt;
        }}

        QLabel {{
            background-color: transparent;
        }}

        QPushButton {{
            background-color: {tokens.colors.surface_secondary};
            color: {tokens.colors.text_primary};
            border: 1px solid {tokens.colors.border_primary};
            border-radius: {tokens.border_radius.md}px;
            padding: {tokens.spacing.xs}px {tokens.spacing.md}px;
            font-size: {tokens.typography.text_sm}pt;
        }}
        QPushButton:hover {{
            background-color: {tokens.colors.surface_tertiary};
        }}
        QPushButton:pressed {{
            border-color: {tokens.colors.border_focus};
        }}
        QPushButton:disabled {{
            background-color: {tokens.colors.background_secondary};
            color: {tokens.colors.text_tertiary};
        }}

        QPushButton#PrimaryButton {{
            background-color: {tokens.colors.primary};
            color: {tokens.colors.text_on_primary};
            border: none;
            font-weight: {tokens.typography.font_semibold};
        }}
        QPushButton#PrimaryButton:hover {{
            background-color: {tokens.colors.primary_hover};
        }}
        QPushButton#PrimaryButton:disabled {{
            background-color: {tokens.colors.primary_disabled};
            color: {tokens.colors.text_tertiary};
        }}

        QLineEdit, QTextEdit, QComboBox {{
            background-color: {tokens.colors.background_secondary};
            color: {tokens.colors.text_primary};
            border: 1px solid {tokens.colors.border_primary};
            border-radius: {tokens.border_radius.md}px;
            padding: {tokens.spacing.xs}px;
            font-size: {tokens.typography.text_sm}pt;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 1px solid {tokens.colors.border_focus};
            background-color: {tokens.colors.background_tertiary};
        }}
        QLineEdit::placeholder {{
            color: {tokens.colors.text_tertiary};
        }}

        QListWidget, QTableView {{
            background-color: {tokens.colors.surface_primary};
            border: 1px solid {tokens.colors.border_primary};
            border-radius: {tokens.border_radius.lg}px;
        }}
        QListWidget::item:selected, QTableView::item:selected {{
            background-color: {tokens.colors.surface_secondary};
        }}

        QHeaderView::section {{
            background-color: {tokens.colors.background_secondary};
            color: {tokens.colors.text_secondary};
            padding: {tokens.spacing.xs}px;
            border: none;
            border-bottom: 1px solid {tokens.colors.border_primary};
            font-weight: {tokens.typography.font_semibold};
            font-size: {tokens.typography.text_sm}pt;
        }}

        QScrollBar:vertical {{
            border: none;
            background: {tokens.colors.surface_primary};
            width: {tokens.spacing.sm}px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {tokens.colors.surface_tertiary};
            min-height: {tokens.spacing.xl}px;
            border-radius: {tokens.border_radius.sm}px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """
