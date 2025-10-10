import uuid
import html
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
    QSplitter, QPushButton, QListWidgetItem, QTextBrowser
)
from PySide6.QtCore import Qt

# UI Imports
from src.ui.add_entry_screen import AddEntryScreen
from src.ui.category_screen import CategoryScreen

# Core Logic Imports
from src.category_manager import CategoryManager

class MainWindow(QMainWindow):
    def __init__(self, vault_data, save_vault_callback):
        super().__init__()
        self.setWindowTitle("PyVault")
        self.setGeometry(100, 100, 1200, 800)

        # Store vault data and the callback to save it
        self.vault_data = vault_data
        self.save_vault_callback = save_vault_callback

        # Initialize CategoryManager with data from the vault
        self.category_manager = CategoryManager()
        self.category_manager.from_dict({"categories": self.vault_data.get("categories", [])})

        # --- UI Setup ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Sidebar for categories
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.addWidget(QLabel("Categories"))
        self.category_list = QListWidget()
        self.sidebar_layout.addWidget(self.category_list)
        self.manage_categories_button = QPushButton("Manage Categories")
        self.sidebar_layout.addWidget(self.manage_categories_button)
        self.splitter.addWidget(self.sidebar)

        # Main content area
        self.main_content = QSplitter(Qt.Vertical)

        # Entries list
        self.entries_widget = QWidget()
        self.entries_layout = QVBoxLayout(self.entries_widget)
        self.entries_toolbar = QHBoxLayout()
        self.entries_label = QLabel("Entries")
        self.add_entry_button = QPushButton("Add Entry")
        self.entries_toolbar.addWidget(self.entries_label)
        self.entries_toolbar.addStretch()
        self.entries_toolbar.addWidget(self.add_entry_button)
        self.entries_layout.addLayout(self.entries_toolbar)
        self.entries_list = QListWidget()
        self.entries_layout.addWidget(self.entries_list)
        self.main_content.addWidget(self.entries_widget)

        # Entry detail view
        self.detail_widget = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_widget)
        self.detail_label = QLabel("Entry Details")
        self.detail_view = QTextBrowser() # Use QTextBrowser for rich text
        self.detail_layout.addWidget(self.detail_label)
        self.detail_layout.addWidget(self.detail_view)
        self.main_content.addWidget(self.detail_widget)

        self.splitter.addWidget(self.main_content)
        self.splitter.setSizes([200, 800])
        self.main_content.setSizes([300, 500])

        # --- Connect Signals ---
        self.manage_categories_button.clicked.connect(self.open_category_dialog)
        self.add_entry_button.clicked.connect(self.open_add_entry_dialog)
        self.entries_list.currentItemChanged.connect(self.display_entry_details)

        # --- Initial Data Load ---
        self.load_categories()
        self.load_entries()

    def load_categories(self):
        self.category_list.clear()
        for category in self.category_manager.get_all_categories():
            item = QListWidgetItem(category.name)
            item.setData(Qt.UserRole, category.id)
            self.category_list.addItem(item)

    def load_entries(self):
        self.entries_list.clear()
        for entry in self.vault_data.get("entries", []):
            item = QListWidgetItem(entry.get("title", "No Title"))
            item.setData(Qt.UserRole, entry.get("id"))
            self.entries_list.addItem(item)

    def display_entry_details(self, current_item, previous_item):
        if not current_item:
            self.detail_view.setHtml("<p>Select an entry to see details.</p>")
            return

        entry_id = current_item.data(Qt.UserRole)
        entry_data = next((e for e in self.vault_data["entries"] if e["id"] == entry_id), None)

        if entry_data:
            # Escape all user-provided data before inserting into HTML
            title = html.escape(entry_data.get('title', ''))
            username = html.escape(entry_data.get('username', ''))
            url = html.escape(entry_data.get('url', ''))
            notes = html.escape(entry_data.get('notes', '')).replace('\n', '<br>')

            details_html = f"""
                <h3>{title}</h3>
                <p><b>Username:</b> {username}</p>
                <p><b>Password:</b> ********</p>
                <p><b>URL:</b> {url}</p>
                <p><b>Notes:</b><br>{notes}</p>
            """
            self.detail_view.setHtml(details_html)
        else:
            self.detail_view.setHtml("<p>Entry details not found.</p>")

    def open_add_entry_dialog(self):
        categories = self.category_manager.get_all_categories()
        dialog = AddEntryScreen(categories, self)
        if dialog.exec():
            entry_data = dialog.get_entry_data()
            entry_data['id'] = str(uuid.uuid4()) # Assign a unique ID
            self.vault_data["entries"].append(entry_data)
            self.load_entries()
            self.save_vault_callback()

    def open_category_dialog(self):
        dialog = CategoryScreen(self.category_manager, self)
        dialog.exec()
        # After closing, the category_manager object is updated.
        # We need to sync this back to our main vault_data and save.
        self.vault_data["categories"] = self.category_manager.to_dict()["categories"]
        self.load_categories()
        self.save_vault_callback()
