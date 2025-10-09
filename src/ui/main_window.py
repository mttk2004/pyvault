"""
PyVault Main Window - Bitwarden Inspired Design
Modern 3-panel layout similar to Bitwarden with dark theme.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QFrame, QLabel, QPushButton, QLineEdit, QListWidget, 
    QListWidgetItem, QScrollArea, QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .design_system import Colors, get_global_stylesheet
from ..category_manager import CategoryManager


class VaultSidebar(QFrame):
    """Left sidebar with navigation options like Bitwarden"""
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(240)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.PRIMARY_BG};
                border-right: 1px solid {Colors.BORDER};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        vault_label = QLabel("Vault")
        vault_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {Colors.PRIMARY_TEXT};
        """)
        header_layout.addWidget(vault_label)
        
        header_layout.addStretch()
        
        new_btn = QPushButton("+ New")
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BLUE_ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {Colors.BLUE_HOVER};
            }}
        """)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        
        # Search
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search...")
        layout.addWidget(search_bar)
        
        # Navigation list
        nav_list = QListWidget()
        nav_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 6px;
                margin: 2px 0px;
                color: {Colors.SECONDARY_TEXT};
            }}
            QListWidget::item:hover {{
                background-color: {Colors.SURFACE_BG};
            }}
            QListWidget::item:selected {{
                background-color: {Colors.BLUE_ACCENT};
                color: white;
            }}
        """)
        
        items = ["All items", "Favorites", "Logins", "Cards", "Secure notes"]
        for item in items:
            nav_list.addItem(item)
            
        layout.addWidget(nav_list)
        layout.addStretch()


class VaultItemList(QFrame):
    """Middle panel showing list of vault items"""
    
    item_selected = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.vault_data = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.SECONDARY_BG};
                border-right: 1px solid {Colors.BORDER};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.SECONDARY_BG};
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title_label = QLabel("All items")
        title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {Colors.PRIMARY_TEXT};
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Items area
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.items_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        layout.addWidget(scroll_area)
        
    def populate_items(self, vault_data):
        """Populate the item list"""
        self.vault_data = vault_data
        
        # Clear existing items
        for i in reversed(range(self.items_layout.count())):
            child = self.items_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
                
        # Add items
        for entry in vault_data:
            item_widget = self.create_item_widget(entry)
            self.items_layout.addWidget(item_widget)
            
        self.items_layout.addStretch()
        
    def create_item_widget(self, entry):
        """Create a single item widget"""
        item = QFrame()
        item.setFixedHeight(60)
        item.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-bottom: 1px solid {Colors.BORDER};
            }}
            QFrame:hover {{
                background-color: {Colors.SURFACE_BG};
            }}
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(20, 12, 20, 12)
        
        # Icon
        icon_label = QLabel("🔐")
        icon_label.setFixedSize(24, 24)
        layout.addWidget(icon_label)
        
        # Content
        content_layout = QVBoxLayout()
        
        service_label = QLabel(entry.get('service', 'Untitled'))
        service_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {Colors.PRIMARY_TEXT};
        """)
        content_layout.addWidget(service_label)
        
        username_label = QLabel(entry.get('username', ''))
        username_label.setStyleSheet(f"""
            font-size: 13px;
            color: {Colors.MUTED_TEXT};
        """)
        content_layout.addWidget(username_label)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Make clickable
        item.mousePressEvent = lambda e: self.item_selected.emit(entry)
        
        return item


class VaultDetailPanel(QFrame):
    """Right panel showing item details"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumWidth(350)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.PRIMARY_BG};
            }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Initially show empty state
        self.show_empty_state()
        
    def show_empty_state(self):
        """Show empty state when no item is selected"""
        self.clear_layout()
        
        empty_label = QLabel("Select an item to view details")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet(f"""
            font-size: 16px;
            color: {Colors.MUTED_TEXT};
            padding: 40px;
        """)
        self.layout.addWidget(empty_label)
        
    def show_item_details(self, item):
        """Show details for selected item"""
        self.clear_layout()
        
        # Service name
        service_label = QLabel(item.get('service', 'Untitled'))
        service_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {Colors.PRIMARY_TEXT};
            margin-bottom: 20px;
        """)
        self.layout.addWidget(service_label)
        
        # Fields
        fields = [
            ("Username", item.get('username', '')),
            ("Password", "••••••••"),
            ("URL", item.get('url', '')),
        ]
        
        for label, value in fields:
            if value:
                field_layout = QVBoxLayout()
                
                label_widget = QLabel(label)
                label_widget.setStyleSheet(f"""
                    font-size: 12px;
                    color: {Colors.MUTED_TEXT};
                    margin-bottom: 4px;
                """)
                field_layout.addWidget(label_widget)
                
                value_widget = QLabel(value)
                value_widget.setStyleSheet(f"""
                    font-size: 14px;
                    color: {Colors.PRIMARY_TEXT};
                    padding: 8px 0px;
                """)
                field_layout.addWidget(value_widget)
                
                self.layout.addLayout(field_layout)
                
        self.layout.addStretch()
        
    def clear_layout(self):
        """Clear all widgets from layout"""
        for i in reversed(range(self.layout.count())):
            child = self.layout.itemAt(i).widget()
            if child:
                child.deleteLater()


class MainWindow(QMainWindow):
    """Main application window with Bitwarden-inspired layout"""
    
    data_changed = Signal()
    lock_requested = Signal()
    
    def __init__(self, category_manager=None):
        super().__init__()
        self.category_manager = category_manager or CategoryManager()
        self.vault_data = []
        
        self.setWindowTitle("PyVault")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI with 3-panel layout"""
        
        # Apply global stylesheet
        self.setStyleSheet(get_global_stylesheet())
        
        # Create splitter for 3-panel layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create panels
        self.sidebar = VaultSidebar()
        self.item_list = VaultItemList()
        self.detail_panel = VaultDetailPanel()
        
        # Add panels to splitter
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.item_list)
        splitter.addWidget(self.detail_panel)
        
        # Set proportions
        splitter.setSizes([240, 500, 350])
        
        # Connect signals
        self.item_list.item_selected.connect(self.detail_panel.show_item_details)
        
        self.setCentralWidget(splitter)
        
    def populate_table(self, data):
        """Populate the vault with data (compatibility)"""
        self.vault_data = data
        self.item_list.populate_items(data)
        
    def get_all_data(self):
        """Get all vault data (compatibility)"""
        return self.vault_data