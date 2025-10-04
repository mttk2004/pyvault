import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, 
    QHeaderView, QAbstractItemView, QLineEdit, QToolBar,
    QStatusBar, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVault - Your Personal Vault")
        self.setMinimumSize(1000, 700)
        
        # Sample data for demo
        self.vault_data = []

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
        self.addToolBar(toolbar)
        
        # Add Entry button
        add_action = QAction("➕ Add Entry", self)
        add_action.triggered.connect(self._add_entry)
        toolbar.addAction(add_action)
        
        # Edit Entry button
        edit_action = QAction("✏️ Edit", self)
        edit_action.triggered.connect(self._edit_entry)
        toolbar.addAction(edit_action)
        
        # Delete Entry button
        delete_action = QAction("🗑️ Delete", self)
        delete_action.triggered.connect(self._delete_entry)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("🔍 Search your vault...")
        self.search_bar.setMaximumWidth(300)
        self.search_bar.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_bar)
        
        toolbar.addSeparator()
        
        # Lock button
        lock_action = QAction("🔒 Lock Vault", self)
        toolbar.addAction(lock_action)

    def _setup_central_widget(self):
        """Sets up the main UI components."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)

        # Table for credentials
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Service", "Username", "Password", "URL"])
        
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
        
        # Context menu
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self._show_context_menu)
        
        # Double click to edit
        self.table_widget.doubleClicked.connect(self._edit_entry)

        self.layout.addWidget(self.table_widget)
        
    def _setup_statusbar(self):
        """Creates the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready | 0 entries")

    def _show_context_menu(self, position):
        """Shows context menu for table items."""
        menu = QMenu()
        
        edit_action = menu.addAction("✏️ Edit")
        edit_action.triggered.connect(self._edit_entry)
        
        delete_action = menu.addAction("🗑️ Delete")
        delete_action.triggered.connect(self._delete_entry)
        
        menu.addSeparator()
        
        copy_user_action = menu.addAction("📋 Copy Username")
        copy_pass_action = menu.addAction("🔑 Copy Password")
        copy_url_action = menu.addAction("🔗 Copy URL")
        
        menu.exec(self.table_widget.viewport().mapToGlobal(position))

    @Slot()
    def _add_entry(self):
        """Opens dialog to add a new entry."""
        # Will be implemented in Step 5
        QMessageBox.information(self, "Add Entry", "This feature will be available in Step 5!")

    @Slot()
    def _edit_entry(self):
        """Opens dialog to edit selected entry."""
        if not self.table_widget.selectedItems():
            QMessageBox.warning(self, "No Selection", "Please select an entry to edit.")
            return
        # Will be implemented in Step 5
        QMessageBox.information(self, "Edit Entry", "This feature will be available in Step 5!")

    @Slot()
    def _delete_entry(self):
        """Deletes the selected entry."""
        if not self.table_widget.selectedItems():
            QMessageBox.warning(self, "No Selection", "Please select an entry to delete.")
            return
        # Will be implemented in Step 5
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this entry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Delete Entry", "This feature will be available in Step 5!")

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
        self.table_widget.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # Service
            service_item = QTableWidgetItem(item.get("service", ""))
            service_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row, 0, service_item)
            
            # Username
            username_item = QTableWidgetItem(item.get("username", ""))
            username_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row, 1, username_item)
            
            # Password (hidden for security)
            password_item = QTableWidgetItem("••••••••")
            password_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row, 2, password_item)
            
            # URL
            url_item = QTableWidgetItem(item.get("url", ""))
            url_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_widget.setItem(row, 3, url_item)
        
        # Update status bar
        self.statusbar.showMessage(f"Ready | {len(data)} entries")

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
