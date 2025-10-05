"""
PyVault Design System
Modern, comprehensive design tokens and theming system.
"""

from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


@dataclass
class ColorPalette:
    """Color palette for theming"""
    # Primary colors
    primary_50: str
    primary_100: str
    primary_200: str
    primary_300: str
    primary_400: str
    primary_500: str
    primary_600: str
    primary_700: str
    primary_800: str
    primary_900: str
    
    # Gray colors
    gray_50: str
    gray_100: str
    gray_200: str
    gray_300: str
    gray_400: str
    gray_500: str
    gray_600: str
    gray_700: str
    gray_800: str
    gray_900: str
    
    # Status colors
    success: str
    warning: str
    error: str
    info: str
    
    # Background colors
    background: str
    surface: str
    surface_hover: str
    surface_active: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_tertiary: str
    text_inverse: str
    
    # Border colors
    border: str
    border_hover: str
    border_focus: str
    
    # Input colors
    input_background: str
    input_border: str
    
    # Status light colors
    success_light: str
    warning_light: str
    error_light: str
    info_light: str
    
    # Status dark colors  
    success_dark: str
    warning_dark: str
    error_dark: str
    info_dark: str
    
    # Status border colors
    error_border: str
    
    # Primary variant
    primary: str
    primary_light: str
    primary_dark: str
    
    # Surface variants
    surface_secondary: str
    
    # Special effects
    shadow: str
    overlay: str


# Light Theme Palette
LIGHT_PALETTE = ColorPalette(
    # Primary (Blue)
    primary_50="#eff6ff",
    primary_100="#dbeafe",
    primary_200="#bfdbfe",
    primary_300="#93c5fd",
    primary_400="#60a5fa",
    primary_500="#3b82f6",
    primary_600="#2563eb",
    primary_700="#1d4ed8",
    primary_800="#1e40af",
    primary_900="#1e3a8a",
    
    # Gray
    gray_50="#f9fafb",
    gray_100="#f3f4f6",
    gray_200="#e5e7eb",
    gray_300="#d1d5db",
    gray_400="#9ca3af",
    gray_500="#6b7280",
    gray_600="#4b5563",
    gray_700="#374151",
    gray_800="#1f2937",
    gray_900="#111827",
    
    # Status
    success="#10b981",
    warning="#f59e0b",
    error="#ef4444",
    info="#06b6d4",
    
    # Background
    background="#ffffff",
    surface="#ffffff",
    surface_hover="#f9fafb",
    surface_active="#f3f4f6",
    
    # Text
    text_primary="#1f2937",
    text_secondary="#6b7280",
    text_tertiary="#9ca3af",
    text_inverse="#ffffff",
    
    # Border
    border="#e5e7eb",
    border_hover="#d1d5db",
    border_focus="#3b82f6",
    
    # Input colors
    input_background="#f9fafb",
    input_border="#e5e7eb",
    
    # Status light colors
    success_light="#ecfdf5",
    warning_light="#fffbeb", 
    error_light="#fef2f2",
    info_light="#f0f9ff",
    
    # Status dark colors
    success_dark="#059669",
    warning_dark="#d97706",
    error_dark="#dc2626",
    info_dark="#0284c7",
    
    # Status border colors
    error_border="#fecaca",
    
    # Primary variant
    primary="#3b82f6",
    primary_light="#dbeafe",
    primary_dark="#1d4ed8",
    
    # Surface variants
    surface_secondary="#f9fafb",
    
    # Effects
    shadow="rgba(0, 0, 0, 0.1)",
    overlay="rgba(0, 0, 0, 0.6)"
)

# Dark Theme Palette
DARK_PALETTE = ColorPalette(
    # Primary (Blue)
    primary_50="#1e3a8a",
    primary_100="#1d4ed8",
    primary_200="#2563eb",
    primary_300="#3b82f6",
    primary_400="#60a5fa",
    primary_500="#93c5fd",
    primary_600="#bfdbfe",
    primary_700="#dbeafe",
    primary_800="#eff6ff",
    primary_900="#f0f9ff",
    
    # Gray
    gray_50="#111827",
    gray_100="#1f2937",
    gray_200="#374151",
    gray_300="#4b5563",
    gray_400="#6b7280",
    gray_500="#9ca3af",
    gray_600="#d1d5db",
    gray_700="#e5e7eb",
    gray_800="#f3f4f6",
    gray_900="#f9fafb",
    
    # Status
    success="#34d399",
    warning="#fbbf24",
    error="#f87171",
    info="#67e8f9",
    
    # Background
    background="#0f172a",
    surface="#1e293b",
    surface_hover="#334155",
    surface_active="#475569",
    
    # Text
    text_primary="#f1f5f9",
    text_secondary="#cbd5e1",
    text_tertiary="#94a3b8",
    text_inverse="#1e293b",
    
    # Border
    border="#334155",
    border_hover="#475569",
    border_focus="#60a5fa",
    
    # Input colors
    input_background="#1e293b",
    input_border="#334155",
    
    # Status light colors
    success_light="#022c22",
    warning_light="#451a03",
    error_light="#450a0a",
    info_light="#0c4a6e",
    
    # Status dark colors
    success_dark="#065f46",
    warning_dark="#92400e",
    error_dark="#991b1b",
    info_dark="#0369a1",
    
    # Status border colors
    error_border="#7f1d1d",
    
    # Primary variant
    primary="#3b82f6",
    primary_light="#dbeafe",
    primary_dark="#1d4ed8",
    
    # Surface variants
    surface_secondary="#334155",
    
    # Effects
    shadow="rgba(0, 0, 0, 0.3)",
    overlay="rgba(0, 0, 0, 0.8)"
)


@dataclass 
class Typography:
    """Typography scale"""
    # Font families
    font_family_sans: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif"
    font_family_mono: str = "'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace"
    
    # Font sizes (in px)
    text_xs: int = 12
    text_sm: int = 14
    text_base: int = 16
    text_lg: int = 18
    text_xl: int = 20
    text_2xl: int = 24
    text_3xl: int = 30
    text_4xl: int = 36
    text_5xl: int = 48
    
    # Heading sizes
    heading_sm: int = 20
    heading_md: int = 24
    heading_lg: int = 32
    heading_xl: int = 40
    
    # Font weights
    font_light: int = 300
    font_normal: int = 400
    font_medium: int = 500
    font_semibold: int = 600
    font_bold: int = 700
    
    # Line heights
    leading_tight: float = 1.25
    leading_normal: float = 1.5
    leading_relaxed: float = 1.625


@dataclass
class Spacing:
    """Spacing system based on 8px grid"""
    # Base unit (8px)
    unit: int = 8
    
    # Spacing scale
    xs: int = 4    # 0.5 * unit
    sm: int = 8    # 1 * unit  
    md: int = 16   # 2 * unit
    lg: int = 24   # 3 * unit
    xl: int = 32   # 4 * unit
    xxl: int = 48  # 6 * unit
    xxxl: int = 64 # 8 * unit


@dataclass
class BorderRadius:
    """Border radius values"""
    none: int = 0
    sm: int = 4
    md: int = 6
    lg: int = 8
    xl: int = 12
    xxl: int = 16
    full: int = 9999


@dataclass
class Shadows:
    """Shadow definitions"""
    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    xl: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    inner: str = "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"


@dataclass
class Transitions:
    """Animation and transition definitions"""
    duration_fast: int = 150
    duration_normal: int = 250
    duration_slow: int = 350
    
    easing_ease_in_out: str = "ease-in-out"
    easing_ease_out: str = "ease-out"
    easing_ease_in: str = "ease-in"


class DesignTokens:
    """Central design tokens"""
    
    def __init__(self, theme: Theme = Theme.LIGHT):
        self.current_theme = theme
        self.colors = LIGHT_PALETTE if theme == Theme.LIGHT else DARK_PALETTE
        self.typography = Typography()
        self.spacing = Spacing()
        self.border_radius = BorderRadius()
        self.shadows = Shadows()
        self.transitions = Transitions()
    
    def switch_theme(self, theme: Theme):
        """Switch between light and dark themes"""
        self.current_theme = theme
        self.colors = LIGHT_PALETTE if theme == Theme.LIGHT else DARK_PALETTE
    
    def get_color(self, color_name: str) -> str:
        """Get color by name"""
        return getattr(self.colors, color_name, self.colors.text_primary)
    
    def get_spacing(self, size: str) -> int:
        """Get spacing by size"""
        return getattr(self.spacing, size, self.spacing.md)


# Global design tokens instance
tokens = DesignTokens()


# Icon definitions (using Unicode symbols for now, can be replaced with custom icons later)
class Icons:
    # Navigation
    MENU = "☰"
    CLOSE = "✕"
    BACK = "←"
    FORWARD = "→"
    
    # Actions
    ADD = "+"
    EDIT = "✎"
    DELETE = "🗑"
    COPY = "📋"
    PASTE = "📋"
    REFRESH = "↻"
    DOWNLOAD = "↓"
    UPLOAD = "↑"
    
    # Security
    LOCK = "🔒"
    UNLOCK = "🔓"
    KEY = "🔑"
    SHIELD = "🛡"
    EYE = "👁"
    EYE_OFF = "🙈"
    
    # Interface
    SEARCH = "🔍"
    FILTER = "⚑"
    SORT = "⇅"
    STAR = "★"
    STAR_EMPTY = "☆"
    HEART = "♥"
    HEART_EMPTY = "♡"
    
    # Status
    CHECK = "✓"
    WARNING = "⚠"
    ERROR = "✕"
    INFO = "ⓘ"
    
    # Arrows
    ARROW_UP = "↑"
    ARROW_DOWN = "↓"
    ARROW_LEFT = "←"
    ARROW_RIGHT = "→"
    CHEVRON_UP = "⌃"
    CHEVRON_DOWN = "⌄"
    CHEVRON_LEFT = "⌃"
    CHEVRON_RIGHT = "⌄"
    
    # Categories
    FOLDER = "📁"
    TAG = "🏷"
    
    # Settings
    GEAR = "⚙"
    SLIDERS = "🎚"
    
    # Communication
    MAIL = "✉"
    PHONE = "📞"
    LINK = "🔗"
    
    # Misc
    HOME = "🏠"
    USER = "👤"
    USERS = "👥"
    CALENDAR = "📅"
    CLOCK = "🕐"
    BELL = "🔔"
    BELL_OFF = "🔕"


def create_glassmorphism_effect(opacity: float = 0.1, blur_radius: int = 10) -> Dict[str, Any]:
    """Create glassmorphism effect properties"""
    return {
        'background_opacity': opacity,
        'blur_radius': blur_radius,
        'border_opacity': 0.2,
        'shadow': 'rgba(0, 0, 0, 0.1)'
    }


def create_neumorphism_effect(is_dark: bool = False) -> Dict[str, Any]:
    """Create neumorphism effect properties"""
    if is_dark:
        return {
            'light_shadow': 'rgba(255, 255, 255, 0.05)',
            'dark_shadow': 'rgba(0, 0, 0, 0.3)',
            'inset_light': 'rgba(255, 255, 255, 0.02)',
            'inset_dark': 'rgba(0, 0, 0, 0.1)'
        }
    else:
        return {
            'light_shadow': 'rgba(255, 255, 255, 0.9)',
            'dark_shadow': 'rgba(0, 0, 0, 0.1)',
            'inset_light': 'rgba(255, 255, 255, 0.5)',
            'inset_dark': 'rgba(0, 0, 0, 0.05)'
        }


# Component style generators
def button_styles(variant: str = "primary") -> str:
    """Generate button styles for different variants"""
    if variant == "primary":
        return f"""
            QPushButton {{
                background-color: {tokens.colors.primary_500};
                color: {tokens.colors.text_inverse};
                border: none;
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.sm}px {tokens.spacing.lg}px;
                font-size: {tokens.typography.text_sm}px;
                font-weight: {tokens.typography.font_medium};
                font-family: {tokens.typography.font_family_sans};
            }}
            QPushButton:hover {{
                background-color: {tokens.colors.primary_600};
            }}
            QPushButton:pressed {{
                background-color: {tokens.colors.primary_700};
            }}
            QPushButton:disabled {{
                background-color: {tokens.colors.gray_300};
                color: {tokens.colors.text_tertiary};
            }}
        """
    elif variant == "secondary":
        return f"""
            QPushButton {{
                background-color: {tokens.colors.surface};
                color: {tokens.colors.text_primary};
                border: 1px solid {tokens.colors.border};
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.sm}px {tokens.spacing.lg}px;
                font-size: {tokens.typography.text_sm}px;
                font-weight: {tokens.typography.font_medium};
                font-family: {tokens.typography.font_family_sans};
            }}
            QPushButton:hover {{
                background-color: {tokens.colors.surface_hover};
                border-color: {tokens.colors.border_hover};
            }}
            QPushButton:pressed {{
                background-color: {tokens.colors.surface_active};
            }}
            QPushButton:disabled {{
                background-color: {tokens.colors.gray_100};
                color: {tokens.colors.text_tertiary};
                border-color: {tokens.colors.gray_200};
            }}
        """
    elif variant == "ghost":
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {tokens.colors.text_secondary};
                border: none;
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.sm}px {tokens.spacing.lg}px;
                font-size: {tokens.typography.text_sm}px;
                font-weight: {tokens.typography.font_medium};
                font-family: {tokens.typography.font_family_sans};
            }}
            QPushButton:hover {{
                background-color: {tokens.colors.surface_hover};
                color: {tokens.colors.text_primary};
            }}
            QPushButton:pressed {{
                background-color: {tokens.colors.surface_active};
            }}
        """


def input_styles() -> str:
    """Generate input field styles"""
    return f"""
        QLineEdit {{
            background-color: {tokens.colors.surface};
            color: {tokens.colors.text_primary};
            border: 1px solid {tokens.colors.border};
            border-radius: {tokens.border_radius.md}px;
            padding: {tokens.spacing.sm}px {tokens.spacing.md}px;
            font-size: {tokens.typography.text_sm}px;
            font-family: {tokens.typography.font_family_sans};
            selection-background-color: {tokens.colors.primary_200};
        }}
        QLineEdit:focus {{
            border-color: {tokens.colors.border_focus};
            outline: none;
        }}
        QLineEdit:disabled {{
            background-color: {tokens.colors.gray_100};
            color: {tokens.colors.text_tertiary};
            border-color: {tokens.colors.gray_200};
        }}
        QLineEdit::placeholder {{
            color: {tokens.colors.text_tertiary};
        }}
    """


def card_styles() -> str:
    """Generate card styles"""
    return f"""
        .card {{
            background-color: {tokens.colors.surface};
            border: 1px solid {tokens.colors.border};
            border-radius: {tokens.border_radius.lg}px;
            box-shadow: {tokens.shadows.sm};
        }}
        .card:hover {{
            box-shadow: {tokens.shadows.md};
            border-color: {tokens.colors.border_hover};
        }}
    """
