"""
Modern stylesheet for PyVault application
Inspired by modern password managers with dark/light theme support
"""

MAIN_STYLESHEET = """
/* Global Styles */
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

QWidget {
    background-color: #f5f5f7;
    color: #1d1d1f;
}

/* Login Window Specific */
QWidget#LoginWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #667eea,
        stop:1 #764ba2
    );
}

QLabel#TitleLabel {
    color: white;
    font-size: 28px;
    font-weight: 600;
    padding: 20px 0px;
}

QLabel#SubtitleLabel {
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
    padding-bottom: 10px;
}

QLabel#PasswordLabel {
    color: white;
    font-size: 14px;
    font-weight: 500;
    padding: 5px 0px;
}

QLineEdit {
    background-color: rgba(255, 255, 255, 0.95);
    border: 2px solid transparent;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    color: #1d1d1f;
}

QLineEdit:focus {
    border: 2px solid #667eea;
    background-color: white;
}

QLineEdit:hover {
    background-color: white;
}

QPushButton {
    background-color: #667eea;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #5568d3;
}

QPushButton:pressed {
    background-color: #4c5fc4;
}

QPushButton:disabled {
    background-color: #d1d1d6;
    color: #86868b;
}

QPushButton#SecondaryButton {
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

QPushButton#SecondaryButton:hover {
    background-color: rgba(255, 255, 255, 0.3);
    border: 2px solid rgba(255, 255, 255, 0.5);
}

QPushButton#DangerButton {
    background-color: #ff3b30;
}

QPushButton#DangerButton:hover {
    background-color: #e6352a;
}

/* Main Window Specific */
QMainWindow {
    background-color: #f5f5f7;
}

QToolBar {
    background-color: white;
    border-bottom: 1px solid #d1d1d6;
    spacing: 8px;
    padding: 8px;
}

QMenuBar {
    background-color: white;
    border-bottom: 1px solid #d1d1d6;
    padding: 4px;
}

QMenuBar::item {
    padding: 6px 12px;
    background-color: transparent;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #e8e8ed;
}

QMenu {
    background-color: white;
    border: 1px solid #d1d1d6;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #667eea;
    color: white;
}

/* Table Widget */
QTableWidget {
    background-color: white;
    border: 1px solid #d1d1d6;
    border-radius: 8px;
    gridline-color: #e8e8ed;
    selection-background-color: #e8eaf6;
    selection-color: #1d1d1f;
}

QTableWidget::item {
    padding: 12px 8px;
    border-bottom: 1px solid #e8e8ed;
}

QTableWidget::item:selected {
    background-color: #e8eaf6;
    color: #1d1d1f;
}

QHeaderView::section {
    background-color: #f5f5f7;
    color: #86868b;
    padding: 12px 8px;
    border: none;
    border-bottom: 2px solid #d1d1d6;
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
}

QHeaderView::section:hover {
    background-color: #e8e8ed;
}

/* Scrollbar */
QScrollBar:vertical {
    border: none;
    background-color: #f5f5f7;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #c7c7cc;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #b0b0b5;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f5f5f7;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #c7c7cc;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #b0b0b5;
}

/* Search Bar */
QLineEdit#SearchBar {
    background-color: #f5f5f7;
    border: 1px solid #d1d1d6;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
}

QLineEdit#SearchBar:focus {
    border: 1px solid #667eea;
    background-color: white;
}

/* Status Bar */
QStatusBar {
    background-color: white;
    border-top: 1px solid #d1d1d6;
    color: #86868b;
    font-size: 12px;
}

/* Dialog */
QDialog {
    background-color: #f5f5f7;
}

/* Group Box */
QGroupBox {
    font-weight: 600;
    border: 2px solid #d1d1d6;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #1d1d1f;
}

/* Error Label */
QLabel#ErrorLabel {
    color: #ff3b30;
    font-size: 13px;
    padding: 8px;
    background-color: rgba(255, 59, 48, 0.1);
    border-radius: 6px;
    border-left: 3px solid #ff3b30;
}

/* Success Label */
QLabel#SuccessLabel {
    color: #34c759;
    font-size: 13px;
    padding: 8px;
    background-color: rgba(52, 199, 89, 0.1);
    border-radius: 6px;
    border-left: 3px solid #34c759;
}
"""

# Dark theme variant (for future use)
DARK_STYLESHEET = """
/* Dark Theme - Coming soon */
"""
