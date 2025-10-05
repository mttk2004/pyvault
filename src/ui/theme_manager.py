"""
PyVault Theme Manager
Handles dynamic theming, animations, and style management.
"""

from typing import Optional, Callable, Dict, Any
from PySide6.QtCore import QObject, Signal, QPropertyAnimation, QEasingCurve, QTimer, QSettings
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPalette, QColor

from .design_system import DesignTokens, Theme, tokens, LIGHT_PALETTE, DARK_PALETTE


class ThemeManager(QObject):
    """Manages application theming and animations"""
    
    theme_changed = Signal(Theme)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("PyVault", "PyVault")
        self.tokens = DesignTokens()
        self.current_theme = Theme.LIGHT
        self.theme_callbacks: Dict[str, Callable] = {}
        self.active_animations: Dict[str, QPropertyAnimation] = {}
        
        # Load theme from settings
        self._load_theme_from_settings()
    
    def initialize(self):
        """Initialize the theme manager"""
        # Apply initial theme
        self._apply_theme_immediately()
    
    def _load_theme_from_settings(self):
        """Load theme preference from settings"""
        theme_name = self.settings.value("theme", "light")
        if theme_name == "dark":
            self.current_theme = Theme.DARK
        elif theme_name == "system":
            self.current_theme = Theme.SYSTEM
            # TODO: Detect system theme
        else:
            self.current_theme = Theme.LIGHT
        
        self.tokens.switch_theme(self.current_theme)
    
    def set_theme(self, theme: Theme, animate: bool = True):
        """Set the application theme"""
        if theme == self.current_theme:
            return
        
        old_theme = self.current_theme
        self.current_theme = theme
        self.tokens.switch_theme(theme)
        
        # Save to settings
        self.settings.setValue("theme", theme.value)
        
        if animate:
            self._animate_theme_transition(old_theme, theme)
        else:
            self._apply_theme_immediately()
        
        self.theme_changed.emit(theme)
    
    def _animate_theme_transition(self, old_theme: Theme, new_theme: Theme):
        """Animate theme transition"""
        # Create fade out/in effect
        app = QApplication.instance()
        if app and hasattr(app, 'activeWindow') and app.activeWindow():
            window = app.activeWindow()
            
            # Fade out
            fade_out = QPropertyAnimation(window, b"windowOpacity", self)
            fade_out.setDuration(200)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.9)
            fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Fade in
            fade_in = QPropertyAnimation(window, b"windowOpacity", self)
            fade_in.setDuration(200)
            fade_in.setStartValue(0.9)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.InCubic)
            
            def apply_theme_and_fade_in():
                self._apply_theme_immediately()
                fade_in.start()
            
            fade_out.finished.connect(apply_theme_and_fade_in)
            fade_out.start()
            
            # Store animations to prevent garbage collection
            self.active_animations["theme_fade_out"] = fade_out
            self.active_animations["theme_fade_in"] = fade_in
    
    def _apply_theme_immediately(self):
        """Apply theme without animation"""
        # Update global tokens
        global tokens
        tokens = self.tokens
        
        # Apply to all registered callbacks
        for callback_id, callback in self.theme_callbacks.items():
            try:
                callback(self.current_theme)
            except Exception as e:
                print(f"Error applying theme to {callback_id}: {e}")
    
    def register_theme_callback(self, callback_id: str, callback: Callable):
        """Register a callback to be called when theme changes"""
        self.theme_callbacks[callback_id] = callback
    
    def register_widget(self, widget: QWidget):
        """Register a widget to receive theme updates"""
        if hasattr(widget, 'on_theme_changed'):
            callback_id = f"widget_{id(widget)}"
            self.register_theme_callback(callback_id, widget.on_theme_changed)
    
    def unregister_theme_callback(self, callback_id: str):
        """Unregister a theme callback"""
        if callback_id in self.theme_callbacks:
            del self.theme_callbacks[callback_id]
    
    def get_current_theme(self) -> Theme:
        """Get current theme"""
        return self.current_theme
    
    def is_dark_theme(self) -> bool:
        """Check if current theme is dark"""
        return self.current_theme == Theme.DARK
    
    def get_color(self, color_name: str) -> str:
        """Get color from current theme"""
        return self.tokens.get_color(color_name)
    
    def get_stylesheet(self) -> str:
        """Get complete application stylesheet"""
        return self.generate_complete_stylesheet()
    
    def generate_complete_stylesheet(self) -> str:
        """Generate complete stylesheet for the application"""
        colors = self.tokens.colors
        typography = self.tokens.typography
        spacing = self.tokens.spacing
        radius = self.tokens.border_radius
        shadows = self.tokens.shadows
        
        return f"""
        /* ===== GLOBAL APPLICATION STYLES ===== */
        QApplication {{
            background-color: {colors.background};
            color: {colors.text_primary};
            font-family: {typography.font_family_sans};
            font-size: {typography.text_base}px;
        }}
        
        /* ===== MAIN WINDOW ===== */
        QMainWindow {{
            background-color: {colors.background};
            color: {colors.text_primary};
        }}
        
        QMainWindow::separator {{
            background-color: {colors.border};
            width: 1px;
            height: 1px;
        }}
        
        /* ===== DIALOGS ===== */
        QDialog {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border-radius: {radius.lg}px;
        }}
        
        /* ===== BUTTONS ===== */
        QPushButton {{
            background-color: {colors.primary_500};
            color: {colors.text_inverse};
            border: none;
            border-radius: {radius.md}px;
            padding: {spacing.sm}px {spacing.lg}px;
            font-size: {typography.text_sm}px;
            font-weight: {typography.font_medium};
            font-family: {typography.font_family_sans};
            min-height: 32px;
        }}
        
        QPushButton:hover {{
            background-color: {colors.primary_600};
        }}
        
        QPushButton:pressed {{
            background-color: {colors.primary_700};
        }}
        
        QPushButton:disabled {{
            background-color: {colors.gray_300};
            color: {colors.text_tertiary};
        }}
        
        QPushButton[variant="secondary"] {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
        }}
        
        QPushButton[variant="secondary"]:hover {{
            background-color: {colors.surface_hover};
            border-color: {colors.border_hover};
        }}
        
        QPushButton[variant="ghost"] {{
            background-color: transparent;
            color: {colors.text_secondary};
        }}
        
        QPushButton[variant="ghost"]:hover {{
            background-color: {colors.surface_hover};
            color: {colors.text_primary};
        }}
        
        /* ===== INPUT FIELDS ===== */
        QLineEdit {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.md}px;
            padding: {spacing.sm}px {spacing.md}px;
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
            selection-background-color: {colors.primary_200};
            min-height: 20px;
        }}
        
        QLineEdit:focus {{
            border-color: {colors.border_focus};
            outline: none;
        }}
        
        QLineEdit:disabled {{
            background-color: {colors.gray_100};
            color: {colors.text_tertiary};
            border-color: {colors.gray_200};
        }}
        
        QLineEdit::placeholder {{
            color: {colors.text_tertiary};
        }}
        
        QTextEdit {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.md}px;
            padding: {spacing.sm}px;
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
            selection-background-color: {colors.primary_200};
        }}
        
        QTextEdit:focus {{
            border-color: {colors.border_focus};
        }}
        
        /* ===== COMBO BOXES ===== */
        QComboBox {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.md}px;
            padding: {spacing.sm}px {spacing.md}px;
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
            min-height: 20px;
        }}
        
        QComboBox:hover {{
            border-color: {colors.border_hover};
        }}
        
        QComboBox:focus {{
            border-color: {colors.border_focus};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: 4px solid transparent;
            border-top: 4px solid {colors.text_secondary};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.md}px;
            selection-background-color: {colors.primary_100};
            outline: none;
        }}
        
        /* ===== CHECKBOXES ===== */
        QCheckBox {{
            color: {colors.text_primary};
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
            spacing: {spacing.sm}px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors.border};
            border-radius: {radius.sm}px;
            background-color: {colors.surface};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors.border_hover};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors.primary_500};
            border-color: {colors.primary_500};
            image: none;
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: {colors.primary_600};
            border-color: {colors.primary_600};
        }}
        
        /* ===== RADIO BUTTONS ===== */
        QRadioButton {{
            color: {colors.text_primary};
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
            spacing: {spacing.sm}px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors.border};
            border-radius: 10px;
            background-color: {colors.surface};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors.primary_500};
            border-color: {colors.primary_500};
        }}
        
        /* ===== SLIDERS ===== */
        QSlider::groove:horizontal {{
            background-color: {colors.gray_200};
            height: 4px;
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors.primary_500};
            border: 2px solid {colors.surface};
            width: 20px;
            height: 20px;
            border-radius: 12px;
            margin: -8px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {colors.primary_600};
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: {colors.primary_500};
            border-radius: 2px;
        }}
        
        /* ===== SPIN BOXES ===== */
        QSpinBox {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.md}px;
            padding: {spacing.sm}px;
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
            min-height: 20px;
        }}
        
        QSpinBox:focus {{
            border-color: {colors.border_focus};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: transparent;
            border: none;
            width: 16px;
        }}
        
        QSpinBox::up-arrow {{
            image: none;
            border: 4px solid transparent;
            border-bottom: 4px solid {colors.text_secondary};
        }}
        
        QSpinBox::down-arrow {{
            image: none;
            border: 4px solid transparent;
            border-top: 4px solid {colors.text_secondary};
        }}
        
        /* ===== TABLES ===== */
        QTableWidget {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.lg}px;
            selection-background-color: {colors.primary_100};
            selection-color: {colors.primary_700};
            gridline-color: {colors.border};
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
        }}
        
        QTableWidget::item {{
            padding: {spacing.md}px {spacing.sm}px;
            border: none;
            border-bottom: 1px solid {colors.border};
        }}
        
        QTableWidget::item:selected {{
            background-color: {colors.primary_100};
            color: {colors.primary_700};
        }}
        
        QTableWidget::item:hover {{
            background-color: {colors.surface_hover};
        }}
        
        QHeaderView::section {{
            background-color: {colors.gray_50};
            color: {colors.text_secondary};
            border: none;
            border-bottom: 2px solid {colors.border};
            padding: {spacing.md}px {spacing.sm}px;
            font-weight: {typography.font_semibold};
            font-size: {typography.text_xs}px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* ===== LISTS ===== */
        QListWidget {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.md}px;
            selection-background-color: {colors.primary_100};
            outline: none;
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
        }}
        
        QListWidget::item {{
            padding: {spacing.md}px;
            border: none;
            border-bottom: 1px solid {colors.border};
        }}
        
        QListWidget::item:selected {{
            background-color: {colors.primary_100};
            color: {colors.primary_700};
        }}
        
        QListWidget::item:hover {{
            background-color: {colors.surface_hover};
        }}
        
        /* ===== TAB WIDGET ===== */
        QTabWidget::pane {{
            background-color: {colors.surface};
            border: 1px solid {colors.border};
            border-radius: {radius.lg}px;
        }}
        
        QTabBar::tab {{
            background-color: {colors.surface};
            color: {colors.text_secondary};
            border: 1px solid {colors.border};
            border-bottom: none;
            border-radius: {radius.md}px {radius.md}px 0 0;
            padding: {spacing.md}px {spacing.xl}px;
            font-size: {typography.text_sm}px;
            font-weight: {typography.font_medium};
            font-family: {typography.font_family_sans};
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors.surface};
            color: {colors.primary_600};
            border-bottom: 2px solid {colors.primary_500};
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors.surface_hover};
            color: {colors.text_primary};
        }}
        
        /* ===== GROUP BOXES ===== */
        QGroupBox {{
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.lg}px;
            margin-top: {spacing.md}px;
            padding-top: {spacing.md}px;
            font-size: {typography.text_sm}px;
            font-weight: {typography.font_semibold};
            font-family: {typography.font_family_sans};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {spacing.md}px;
            padding: 0 {spacing.sm}px;
            background-color: {colors.surface};
        }}
        
        /* ===== LABELS ===== */
        QLabel {{
            color: {colors.text_primary};
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
        }}
        
        QLabel[role="heading"] {{
            font-size: {typography.text_lg}px;
            font-weight: {typography.font_semibold};
            color: {colors.text_primary};
        }}
        
        QLabel[role="subheading"] {{
            font-size: {typography.text_base}px;
            font-weight: {typography.font_medium};
            color: {colors.text_secondary};
        }}
        
        QLabel[role="caption"] {{
            font-size: {typography.text_xs}px;
            color: {colors.text_tertiary};
        }}
        
        /* ===== MENU BAR ===== */
        QMenuBar {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border-bottom: 1px solid {colors.border};
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
        }}
        
        QMenuBar::item {{
            padding: {spacing.sm}px {spacing.md}px;
            background-color: transparent;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors.surface_hover};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {colors.surface_active};
        }}
        
        /* ===== MENUS ===== */
        QMenu {{
            background-color: {colors.surface};
            color: {colors.text_primary};
            border: 1px solid {colors.border};
            border-radius: {radius.md}px;
            padding: {spacing.xs}px;
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
        }}
        
        QMenu::item {{
            padding: {spacing.sm}px {spacing.md}px;
            border-radius: {radius.sm}px;
            margin: 1px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors.primary_100};
            color: {colors.primary_700};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {colors.border};
            margin: {spacing.xs}px 0;
        }}
        
        /* ===== STATUS BAR ===== */
        QStatusBar {{
            background-color: {colors.surface};
            color: {colors.text_secondary};
            border-top: 1px solid {colors.border};
            font-size: {typography.text_xs}px;
            font-family: {typography.font_family_sans};
            padding: {spacing.xs}px {spacing.md}px;
        }}
        
        /* ===== TOOL BAR ===== */
        QToolBar {{
            background-color: {colors.surface};
            border: none;
            border-bottom: 1px solid {colors.border};
            spacing: {spacing.xs}px;
            padding: {spacing.sm}px;
        }}
        
        QToolButton {{
            background-color: transparent;
            color: {colors.text_secondary};
            border: none;
            border-radius: {radius.md}px;
            padding: {spacing.sm}px;
            font-size: {typography.text_sm}px;
            font-family: {typography.font_family_sans};
        }}
        
        QToolButton:hover {{
            background-color: {colors.surface_hover};
            color: {colors.text_primary};
        }}
        
        QToolButton:pressed {{
            background-color: {colors.surface_active};
        }}
        
        /* ===== SCROLL BARS ===== */
        QScrollBar:vertical {{
            background-color: {colors.surface};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors.gray_300};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors.gray_400};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors.surface};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors.gray_300};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors.gray_400};
        }}
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        
        /* ===== SPLITTER ===== */
        QSplitter::handle {{
            background-color: {colors.border};
        }}
        
        QSplitter::handle:horizontal {{
            width: 1px;
        }}
        
        QSplitter::handle:vertical {{
            height: 1px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors.primary_300};
        }}
        
        /* ===== PROGRESS BAR ===== */
        QProgressBar {{
            background-color: {colors.gray_200};
            border: none;
            border-radius: {radius.sm}px;
            height: 8px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors.primary_500};
            border-radius: {radius.sm}px;
        }}
        """


# Global theme manager instance
theme_manager = ThemeManager()


def apply_theme_to_widget(widget: QWidget, theme: Theme):
    """Apply theme to a specific widget"""
    widget.setStyleSheet(theme_manager.get_stylesheet())


def create_fade_animation(widget: QWidget, duration: int = 200, start_value: float = 0.0, end_value: float = 1.0) -> QPropertyAnimation:
    """Create a fade animation for a widget"""
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(start_value)
    animation.setEndValue(end_value)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    return animation


def create_slide_animation(widget: QWidget, start_pos: tuple, end_pos: tuple, duration: int = 300) -> QPropertyAnimation:
    """Create a slide animation for a widget"""
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setStartValue(start_pos)
    animation.setEndValue(end_pos)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    return animation
