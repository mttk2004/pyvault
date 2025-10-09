"""
PyVault Design System - Bitwarden Inspired
"""

# Color constants inspired by Bitwarden
class Colors:
    # Backgrounds
    PRIMARY_BG = "#1A1D29"
    SECONDARY_BG = "#242937" 
    SURFACE_BG = "#2F3349"
    CARD_BG = "#363B52"
    
    # Text
    PRIMARY_TEXT = "#FFFFFF"
    SECONDARY_TEXT = "#C7D0DD"
    MUTED_TEXT = "#8996A8"
    
    # Accent
    BLUE_ACCENT = "#175DDC"
    BLUE_HOVER = "#1252C4"
    
    # Borders
    BORDER = "#3F4561"
    BORDER_LIGHT = "#4A5068"
    
    # Status
    SUCCESS = "#00A651"
    ERROR = "#E53E3E"
    WARNING = "#F6AD55"


def get_global_stylesheet():
    """Get global stylesheet for the application"""
    return f"""
    QWidget {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        color: {Colors.PRIMARY_TEXT};
        background-color: {Colors.PRIMARY_BG};
    }}
    
    QPushButton {{
        background-color: {Colors.BLUE_ACCENT};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        min-height: 32px;
    }}
    
    QPushButton:hover {{
        background-color: {Colors.BLUE_HOVER};
    }}
    
    QLineEdit {{
        background-color: {Colors.SURFACE_BG};
        color: {Colors.PRIMARY_TEXT};
        border: 1px solid {Colors.BORDER};
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 14px;
    }}
    
    QLineEdit:focus {{
        border-color: {Colors.BLUE_ACCENT};
    }}
    """