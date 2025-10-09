"""
PyVault Main Window - V2 (Bitwarden Inspired)
A complete rewrite featuring a three-panel dark-themed layout.
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QPushButton,
    QHeaderView, QAbstractItemView, QLineEdit, QToolBar,
    QStatusBar, QMessageBox, QMenu, QSplitter, QListWidget, QListWidgetItem,
    QLabel, QFrame, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, Slot, Signal, QTimer, QSize
from PySide6.QtGui import QAction, QKeySequence, QFont, QColor, QIcon

from .design_system import tokens, get_global_stylesheet
from .entry_dialog import EntryDialog
from .category_dialog import CategoryDialog
from .toast_notification import show_success_toast, show_error_toast, show_warning_toast, show_info_toast
from ..category_manager import CategoryManager, Category
from .table_model import EntryTableModel

class MainWindow(QMainWindow):
    """The main application window with a three-panel layout."""

    data_changed = Signal()
    lock_requested = Signal()
    categories_changed = Signal()

    def __init__(self, category_manager=None):
        super().__init__()
        self.category_manager = category_manager or CategoryManager()
        self.vault_data = []
        self.filtered_data = []
        self.current_category_filter = "ALL"  # "ALL" or a category ID

        self.setWindowTitle("PyVault")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        self._setup_ui()
        self.setStyleSheet(get_global_stylesheet())
        # self._update_detail_view(None) # Start with empty detail view - TODO: implement this method

    def _setup_ui(self):
        """Setup the main UI components."""
        # --- Toolbar ---
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ffffff;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                padding: 10px;
                spacing: 10px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-weight: 500;
                color: #333333;
            }
            QToolButton:hover {
                background-color: #f5f5f5;
            }
            QToolButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        self.addToolBar(toolbar)

        # Add Entry button
        add_action = QAction(QIcon("src/assets/icons/plus-circle.svg"), "Add Entry", self)
        add_action.triggered.connect(self._add_entry)
        toolbar.addAction(add_action)

        # Edit Entry button
        edit_action = QAction(QIcon("src/assets/icons/edit.svg"), "Edit", self)
        edit_action.triggered.connect(self._edit_entry)
        toolbar.addAction(edit_action)

        # Delete Entry button
        delete_action = QAction(QIcon("src/assets/icons/trash-2.svg"), "Delete", self)
        delete_action.triggered.connect(self._delete_entry)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setMaximumWidth(250)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #007aff;
                background-color: #ffffff;
            }
        """)
        self.search_bar.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_bar)

        # Manage Categories button
        categories_action = QAction(QIcon("src/assets/icons/tag.svg"), "Categories", self)
        categories_action.triggered.connect(self._manage_categories)
        toolbar.addAction(categories_action)

        toolbar.addSeparator()

        # Lock button
        lock_action = QAction(QIcon("src/assets/icons/lock.svg"), "Lock Vault", self)
        lock_action.triggered.connect(self.lock_requested)
        toolbar.addAction(lock_action)

        # --- Central Widget (Splitter) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        # Create sidebar and main content
        self._setup_category_sidebar()
        self._setup_main_content()

    def _setup_category_sidebar(self):
        """Create the category sidebar."""
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(20)

        # Categories title
        title_label = QLabel("Categories")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #333333;
            padding-bottom: 10px;
        """)
        sidebar_layout.addWidget(title_label)

        # Category list
        self.category_list = QListWidget()
        self.category_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                border-radius: 6px;
                padding: 12px 16px;
                margin: 2px 0;
                font-size: 14px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #007aff;
                font-weight: 500;
            }
        """)
        self.category_list.itemClicked.connect(self._on_category_filter_changed)
        sidebar_layout.addWidget(self.category_list)

        sidebar_layout.addStretch()

        self.splitter.addWidget(sidebar)

    def _setup_main_content(self):
        """Create the main content area."""
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        self.layout.setContentsMargins(20, 16, 20, 16)
        self.layout.setSpacing(16)

        # Add current view title
        self.view_title = QLabel("All Entries")
        self.view_title.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #333333;
            padding: 10px 0;
        """)
        self.layout.addWidget(self.view_title)

        self._setup_entries_table()

        self.splitter.addWidget(content_widget)

        # Set splitter proportions
        self.splitter.setSizes([280, 800])

    def _setup_entries_table(self):
        """Setup the entries table."""
        # Table for credentials
        self.table_view = QTableView()
        self.table_model = EntryTableModel(
            headers=["Category", "Service", "Username", "Password", "URL"],
            category_manager=self.category_manager
        )
        self.table_view.setModel(self.table_model)

        # Modern table styling
        self.table_view.setStyleSheet("""
            QTableView {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f5f5f5;
                selection-background-color: #e3f2fd;
                font-size: 13px;
            }
            QTableView::item {
                padding: 12px 8px;
                border: none;
            }
            QTableView::item:selected {
                background-color: #e3f2fd;
                color: #007aff;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #6c757d;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QTableView::item:alternate {
                background-color: #f8f9fa;
            }
        """)

        # Style the table
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setShowGrid(False)

        # Context menu
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._show_context_menu)

        # Double click to edit
        self.table_view.doubleClicked.connect(self._edit_entry)

        # Empty state label
        self.empty_state_label = QLabel(
            "No entries found. Click '+ Add Entry' to get started.",
            self.table_view
        )
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state_label.setStyleSheet("""
            font-size: 16px;
            color: #6c757d;
        """)
        self.empty_state_label.hide()

        self.layout.addWidget(self.table_view)

    def _setup_statusbar(self):
        """Creates the status bar."""
        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #e0e0e0;
                color: #6c757d;
                font-size: 12px;
                padding: 4px 16px;
            }
        """)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready | 0 entries")

    def _show_context_menu(self, position):
        """Shows context menu for table items."""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 8px 16px;
                color: #333333;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #f5f5f5;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 8px;
            }
        """)

        edit_action = menu.addAction("Edit Entry")
        edit_action.triggered.connect(self._edit_entry)

        delete_action = menu.addAction("Delete Entry")
        delete_action.triggered.connect(self._delete_entry)

        menu.addSeparator()

        copy_user_action = menu.addAction("Copy Username")
        copy_user_action.triggered.connect(self._copy_username)

        copy_pass_action = menu.addAction("Copy Password")
        copy_pass_action.triggered.connect(self._copy_password)

        copy_url_action = menu.addAction("Copy URL")
        copy_url_action.triggered.connect(self._copy_url)

        menu.addSeparator()

        # Category submenu
        category_menu = menu.addMenu("Move to Category")
        categories = self.category_manager.get_all_categories()
        for category in categories:
            category_action = category_menu.addAction(category.name)
            category_action.triggered.connect(lambda checked, cat_id=category.id: self._move_entry_to_category(cat_id))

        menu.exec(self.table_view.viewport().mapToGlobal(position))

    @Slot()
    def _add_entry(self):
        """Opens dialog to add a new entry."""
        dialog = EntryDialog(self, category_manager=self.category_manager)
        dialog.entry_saved.connect(self._save_new_entry)
        dialog.exec()

    @Slot()
    def _edit_entry(self):
        """Opens dialog to edit selected entry."""
        selected_row = self.table_view.currentIndex().row()
        if selected_row < 0:
            show_warning_toast("Please select an entry to edit.", parent=self)
            return

        entry_data = self.filtered_data[selected_row]
        original_row = self.vault_data.index(entry_data)

        dialog = EntryDialog(self, entry_data=entry_data, category_manager=self.category_manager)
        dialog.entry_saved.connect(lambda updated_entry: self._save_edited_entry(original_row, updated_entry))
        dialog.exec()

    @Slot()
    def _delete_entry(self):
        """Deletes the selected entry."""
        selected_row = self.table_view.currentIndex().row()
        if selected_row < 0:
            show_warning_toast("Please select an entry to delete.", parent=self)
            return

        entry_data = self.filtered_data[selected_row]
        original_row = self.vault_data.index(entry_data)

        entry = self.vault_data[original_row]
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the entry for <b>{entry.get('service', '')}</b>?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            service_name = entry.get('service', 'entry')
            del self.vault_data[original_row]
            self._refresh_ui()
            self.data_changed.emit()
            show_success_toast(f"Deleted entry for {service_name}", parent=self)

        title = QLabel("Categories")
        title.setStyleSheet(f"font-size: {tokens.typography.text_lg}pt; font-weight: {tokens.typography.font_semibold};")

        self.vault_data.append(entry)
        self._refresh_ui()
        self.data_changed.emit()
        show_success_toast(f"Added new entry for {entry.get('service', 'service')}", parent=self)

    @Slot()
    def _save_edited_entry(self, row: int, updated_entry: dict):
        # Ensure entry has a category
        if "category" not in updated_entry:
            updated_entry["category"] = CategoryManager.UNCATEGORIZED_ID

        # Update the entry directly
        if 0 <= row < len(self.vault_data):
            self.vault_data[row] = updated_entry

        self._refresh_ui()
        self.data_changed.emit()
        show_success_toast(f"Updated entry for {updated_entry.get('service', 'service')}", parent=self)

    @Slot()
    def _copy_username(self):
        selected_row = self.table_view.currentIndex().row()
        if selected_row < 0: return

        entry = self.filtered_data[selected_row]
        username = entry.get("username", "")
        self._copy_to_clipboard(username, "Username")

    @Slot()
    def _copy_password(self):
        selected_row = self.table_view.currentIndex().row()
        if selected_row < 0: return

        entry = self.filtered_data[selected_row]
        password = entry.get("password", "")
        self._copy_to_clipboard(password, "Password")

    @Slot()
    def _copy_url(self):
        selected_row = self.table_view.currentIndex().row()
        if selected_row < 0: return

        entry = self.filtered_data[selected_row]
        url = entry.get("url", "")
        self._copy_to_clipboard(url, "URL")

    def _copy_to_clipboard(self, text: str, item_name: str):
        """Copies text to clipboard and starts a timer to clear it."""
        if not text:
            show_warning_toast(f"No {item_name.lower()} to copy", parent=self)
            return
        QApplication.clipboard().setText(text)
        show_success_toast(f"{item_name} copied to clipboard", duration=2000, parent=self)
        self.clipboard_timer.start(30000) # 30 seconds

    @Slot()
    def _clear_clipboard(self):
        """Clears the clipboard."""
        current_text = QApplication.clipboard().text()
        if not current_text:
            return

        is_sensitive = any(
            current_text == entry.get("password") or current_text == entry.get("username")
            for entry in self.vault_data
        )

        if is_sensitive:
            QApplication.clipboard().clear()
            show_info_toast("Clipboard cleared for security", parent=self)

    @Slot()
    def _filter_table(self, text):
        """Filters table based on search text."""
        if not text:
            self.table_model.set_data(self.filtered_data)
            return

        search_text = text.lower()
        filtered = [
            entry for entry in self.filtered_data
            if any(search_text in str(value).lower() for value in entry.values())
        ]
        self.table_model.set_data(filtered)

    @Slot()
    def _show_about(self):
        """Shows about dialog."""
        QMessageBox.about(
            self,
            "About PyVault",
            "<h3>PyVault</h3>"
            "<p>A secure, local password manager built with Python and PySide6.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>AES-256-GCM encryption</li>"
            "<li>PBKDF2 key derivation</li>"
            "<li>100% local storage</li>"
            "</ul>"
            "<p>Version 1.0.0</p>"
        )

    def populate_table(self, data: list[dict]):
        """
        Populates the table with decrypted vault data.
        """
        self.vault_data = data
        self._refresh_ui()

    def _refresh_ui(self):
        self._populate_category_sidebar()
        self._apply_current_filter()

    def _populate_category_sidebar(self):
        self.category_list.clear()
        counts = self.category_manager.count_entries_by_category(self.vault_data)

        entry_counts = self.category_manager.count_entries_by_category(self.vault_data)

        all_item = QListWidgetItem()
        all_item.setText(f"● All Entries ({len(self.vault_data)})")
        all_item.setData(Qt.ItemDataRole.UserRole, "ALL")
        all_item.setForeground(QColor("#6c757d"))
        self.category_list.addItem(all_item)

        categories = self.category_manager.get_all_categories()
        for category in categories:
            count = entry_counts.get(category.id, 0)
            item = QListWidgetItem()
            item.setText(f"● {category.name} ({count})")
            item.setData(Qt.ItemDataRole.UserRole, category.id)
            item.setForeground(QColor(category.color))
            self.category_list.addItem(item)

        self._select_category_in_sidebar(self.current_category_filter)

    def _select_category_in_sidebar(self, category_id):
        """Select a category in the sidebar."""
        for i in range(self.category_list.count()):
            if self.category_list.item(i).data(Qt.ItemDataRole.UserRole) == self.current_category_filter:
                self.category_list.setCurrentRow(i)
                break

    def _apply_current_filter(self):
        """Apply the current category filter to the table."""
        if self.current_category_filter is None:
            self.filtered_data = self.vault_data.copy()
            self.view_title.setText("All Entries")
        else:
            category = self.category_manager.get_category(self.current_category_filter)
            if category:
                self.filtered_data = [
                    entry for entry in self.vault_data
                    if entry.get("category", CategoryManager.UNCATEGORIZED_ID) == self.current_category_filter
                ]
                self.view_title.setText(category.name)
            else:
                self.filtered_data = []
                self.view_title.setText("Unknown Category")

        self._populate_table_with_data(self.filtered_data)

    def _populate_table_with_data(self, data: list[dict]):
        """Populate table with the given data."""
        self.table_model.set_data(data)
        self._update_empty_state()

    def _update_empty_state(self):
        """Show or hide the empty state label."""
        if self.table_model.rowCount() == 0:
            self.empty_state_label.show()
        else:
            self.empty_state_label.hide()

    def resizeEvent(self, event):
        """Handle window resize to keep empty state label centered."""
        super().resizeEvent(event)
        self._center_empty_state_label()

    def _center_empty_state_label(self):
        """Center the empty state label within the table view."""
        if self.empty_state_label:
            rect = self.table_view.viewport().rect()
            self.empty_state_label.setGeometry(rect)

    def _update_status_bar(self):
        """Update the status bar with current info."""
        total_entries = len(self.vault_data)
        filtered_entries = len(self.filtered_data)

        if self.current_category_filter is None:
            self.statusbar.showMessage(f"Ready | {total_entries} entries")
        else:
            category = self.category_manager.get_category(self.current_category_filter)
            category_name = category.name if category else "Unknown"
            self.statusbar.showMessage(f"Ready | {filtered_entries} entries in {category_name} | {total_entries} total")

    @Slot()
    def _on_category_filter_changed(self, item: QListWidgetItem):
        self.current_category_filter = item.data(Qt.ItemDataRole.UserRole)
        self._apply_current_filter()

    @Slot()
    def _add_entry(self):
        dialog = EntryDialog(self, category_manager=self.category_manager)
        if dialog.exec():
            entry = dialog.get_entry_data()
            self.vault_data.append(entry)
            self.data_changed.emit()
            self._refresh_ui()

    @Slot()
    def _on_categories_changed(self):
        """Handle changes to categories."""
        self._refresh_ui()
        self.categories_changed.emit()

    def _move_entry_to_category(self, category_id: str):
        """Move selected entry to a different category."""
        selected_row = self.table_view.currentIndex().row()
        if selected_row < 0:
            show_warning_toast("Please select an entry to move", parent=self)
            return

        entry_data = self.filtered_data[selected_row]
        original_row = self.vault_data.index(entry_data)

        entry = self.vault_data[original_row]
        self.vault_data[original_row]["category"] = category_id

        category = self.category_manager.get_category(category_id)
        category_name = category.name if category else "Uncategorized"
        service_name = entry.get('service', 'entry')

        self._refresh_ui()
        self.data_changed.emit()
        show_success_toast(f"Moved {service_name} to {category_name}", parent=self)

    def get_all_data(self) -> list[dict]:
        """Returns the current state of the vault data."""
        return self.vault_data

    def _manage_categories(self):
        """Open the category management dialog."""
        from .category_dialog import CategoryDialog
        dialog = CategoryDialog(self.category_manager, self.vault_data, self)
        dialog.categories_changed.connect(self._on_categories_changed)
        dialog.exec()

    def _on_categories_changed(self):
        """Handle changes to categories."""
        self._refresh_category_sidebar()
        self._refresh_ui()
        self.data_changed.emit()

    def _refresh_category_sidebar(self):
        """Refresh the category sidebar with updated categories."""
        # Clear existing category items
        for i in reversed(range(1, self.sidebar_layout.count())):  # Skip "All" button
            item = self.sidebar_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                self.sidebar_layout.removeItem(item)

        # Re-add updated categories
        self._populate_category_sidebar()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    category_manager = CategoryManager()
    test_data = [
        {"service": "Google", "username": "test@gmail.com", "password": "123", "url": "google.com", "category": "uncategorized"},
        {"service": "GitHub", "username": "test-user", "password": "456", "url": "github.com", "category": "uncategorized"},
    ]
    main_win = MainWindow(category_manager)
    main_win.populate_table(test_data)
    main_win.show()
    sys.exit(app.exec())
