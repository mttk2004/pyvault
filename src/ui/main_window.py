import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QAbstractItemView, QLineEdit, QToolBar,
    QStatusBar, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Slot, Signal, QTimer
from PySide6.QtGui import QAction, QKeySequence

from .entry_dialog import EntryDialog

class MainWindow(QMainWindow):
    data_changed = Signal()
    lock_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVault - Your Personal Vault")
        self.setMinimumSize(1000, 700)

        self.vault_data = []
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.setSingleShot(True)
        self.clipboard_timer.timeout.connect(self._clear_clipboard)

        self._setup_menubar()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_statusbar()

    def _setup_menubar(self):
        """Creates the menu bar."""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Entry", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._add_entry)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        lock_action = QAction("&Lock Vault", self)
        lock_action.setShortcut(QKeySequence("Ctrl+L"))
        lock_action.triggered.connect(self.lock_requested)
        file_menu.addAction(lock_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        edit_action = QAction("&Edit Entry", self)
        edit_action.setShortcut(QKeySequence("Ctrl+E"))
        edit_action.triggered.connect(self._edit_entry)
        edit_menu.addAction(edit_action)

        delete_action = QAction("&Delete Entry", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self._delete_entry)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        copy_user_action = QAction("Copy &Username", self)
        copy_user_action.setShortcut(QKeySequence("Ctrl+Shift+U"))
        edit_menu.addAction(copy_user_action)

        copy_pass_action = QAction("Copy &Password", self)
        copy_pass_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        edit_menu.addAction(copy_pass_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About PyVault", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        """Creates the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #e9ecef;
                padding: 8px 16px;
                spacing: 8px;
            }
            QToolButton {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #495057;
            }
            QToolButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QToolButton:pressed {
                background-color: #dee2e6;
            }
        """)
        self.addToolBar(toolbar)

        # Add Entry button
        add_action = QAction("+ Add Entry", self)
        add_action.triggered.connect(self._add_entry)
        toolbar.addAction(add_action)

        # Edit Entry button
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self._edit_entry)
        toolbar.addAction(edit_action)

        # Delete Entry button
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self._delete_entry)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search your vault...")
        self.search_bar.setMaximumWidth(300)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #007aff;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #adb5bd;
            }
        """)
        self.search_bar.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_bar)

        toolbar.addSeparator()

        # Lock button
        lock_action = QAction("Lock Vault", self)
        lock_action.triggered.connect(self.lock_requested)
        toolbar.addAction(lock_action)

    def _setup_central_widget(self):
        """Sets up the main UI components."""
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 16, 20, 16)
        self.layout.setSpacing(16)

        # Table for credentials
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Service", "Username", "Password", "URL"])

        # Modern table styling
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #f1f3f5;
                selection-background-color: #e3f2fd;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 2px solid #dee2e6;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #495057;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                background-color: #f1f3f5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #adb5bd;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6c757d;
            }
        """)

        # Style the table
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setShowGrid(False)

        # Context menu
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self._show_context_menu)

        # Double click to edit
        self.table_widget.doubleClicked.connect(self._edit_entry)

        self.layout.addWidget(self.table_widget)

    def _setup_statusbar(self):
        """Creates the status bar."""
        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
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
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 8px 16px;
                color: #495057;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #e9ecef;
            }
            QMenu::separator {
                height: 1px;
                background-color: #dee2e6;
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

        menu.exec(self.table_widget.viewport().mapToGlobal(position))

    @Slot()
    def _add_entry(self):
        """Opens dialog to add a new entry."""
        dialog = EntryDialog(self)
        dialog.entry_saved.connect(self._save_new_entry)
        dialog.exec()

    @Slot()
    def _edit_entry(self):
        """Opens dialog to edit selected entry."""
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an entry to edit.")
            return

        entry_data = self.vault_data[selected_row]

        dialog = EntryDialog(self, entry_data=entry_data)
        dialog.entry_saved.connect(lambda updated_entry: self._save_edited_entry(selected_row, updated_entry))
        dialog.exec()

    @Slot()
    def _delete_entry(self):
        """Deletes the selected entry."""
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an entry to delete.")
            return

        entry = self.vault_data[selected_row]
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the entry for <b>{entry.get('service', '')}</b>?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.vault_data[selected_row]
            self.populate_table(self.vault_data)
            self.data_changed.emit()

    @Slot()
    def _save_new_entry(self, entry: dict):
        self.vault_data.append(entry)
        self.populate_table(self.vault_data)
        self.data_changed.emit()

    @Slot()
    def _save_edited_entry(self, row: int, updated_entry: dict):
        self.vault_data[row] = updated_entry
        self.populate_table(self.vault_data)
        self.data_changed.emit()

    @Slot()
    def _copy_username(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: return
        username = self.vault_data[selected_row].get("username", "")
        self._copy_to_clipboard(username, "Username")

    @Slot()
    def _copy_password(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: return
        password = self.vault_data[selected_row].get("password", "")
        self._copy_to_clipboard(password, "Password")

    @Slot()
    def _copy_url(self):
        selected_row = self.table_widget.currentRow()
        if selected_row < 0: return
        url = self.vault_data[selected_row].get("url", "")
        self._copy_to_clipboard(url, "URL")

    def _copy_to_clipboard(self, text: str, item_name: str):
        """Copies text to clipboard and starts a timer to clear it."""
        if not text:
            return
        QApplication.clipboard().setText(text)
        self.statusbar.showMessage(f"{item_name} copied to clipboard. Will be cleared in 30 seconds.", 5000)
        self.clipboard_timer.start(30000) # 30 seconds

    @Slot()
    def _clear_clipboard(self):
        """Clears the clipboard."""
        # Check if the clipboard content is still what we put there, to avoid clearing user's own copies.
        # This is a simple check; more robust solutions might be needed for complex scenarios.
        # For this app's purpose, it's a good enough guard.
        current_text = QApplication.clipboard().text()
        is_sensitive = False
        for entry in self.vault_data:
            if current_text and (current_text == entry.get("password") or current_text == entry.get("username")):
                is_sensitive = True
                break

        if is_sensitive:
            QApplication.clipboard().clear()
            self.statusbar.showMessage("Clipboard cleared for security.", 3000)

    @Slot()
    def _filter_table(self, text):
        """Filters table based on search text."""
        for row in range(self.table_widget.rowCount()):
            match = False
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table_widget.setRowHidden(row, not match)

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
        Each item in the list is a dictionary with 'service', 'username', 'password', 'url'.
        """
        self.vault_data = data
        self.table_widget.setRowCount(0) # Clear table before populating
        self.table_widget.setRowCount(len(data))

        for row, item in enumerate(data):
            # Store original index in a hidden way
            service_item = QTableWidgetItem(item.get("service", ""))
            service_item.setData(Qt.ItemDataRole.UserRole, row)
            self.table_widget.setItem(row, 0, service_item)

            # Username
            username_item = QTableWidgetItem(item.get("username", ""))
            self.table_widget.setItem(row, 1, username_item)

            # Password (hidden for security)
            password_item = QTableWidgetItem("••••••••")
            password_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row, 2, password_item)

            # URL
            url_item = QTableWidgetItem(item.get("url", ""))
            self.table_widget.setItem(row, 3, url_item)

        # Update status bar
        self.statusbar.showMessage(f"Ready | {len(data)} entries")

    def get_all_data(self) -> list[dict]:
        """Returns the current state of the vault data."""
        return self.vault_data

# Example usage for testing the UI component directly
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Example data
    test_data = [
        {"service": "Google", "username": "test@gmail.com", "password": "123", "url": "google.com"},
        {"service": "GitHub", "username": "test-user", "password": "456", "url": "github.com"},
    ]

    main_win = MainWindow()
    main_win.populate_table(test_data)
    main_win.show()

    sys.exit(app.exec())
