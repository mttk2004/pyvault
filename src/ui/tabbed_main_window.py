"""
Modern Tab-based Main Window for PyVault
Provides a unified interface with Vault, Generator, and Settings tabs.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QTabWidget,
    QHeaderView, QAbstractItemView, QLineEdit, QToolBar,
    QStatusBar, QMessageBox, QMenu, QSplitter, QListWidget, QListWidgetItem,
    QLabel, QFrame, QGroupBox, QScrollArea, QFormLayout, QTextEdit,
    QCheckBox, QSpinBox, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, Slot, Signal, QTimer, QSize
from PySide6.QtGui import QAction, QKeySequence, QFont, QIcon

from .entry_dialog import EntryDialog
from .category_dialog import CategoryDialog
from .password_generator_widget import PasswordGeneratorWidget
from ..category_manager import CategoryManager, Category


class VaultTab(QWidget):
    """Tab containing the password vault with entries and categories."""
    
    data_changed = Signal()
    categories_changed = Signal()
    
    def __init__(self, category_manager=None, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager or CategoryManager()
        self.vault_data = []
        self.filtered_data = []
        self.current_category_filter = None
        self.clipboard_timer = QTimer(self)
        self.clipboard_timer.setSingleShot(True)
        self.clipboard_timer.timeout.connect(self._clear_clipboard)
        
        self._setup_ui()
        self._populate_category_list()
    
    def _setup_ui(self):
        """Setup the vault tab UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create horizontal splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Create sidebar and main content
        self._setup_category_sidebar()
        self._setup_main_content()
    
    def _setup_category_sidebar(self):
        """Create the category sidebar."""
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: white;
                border-right: 1px solid #dee2e6;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.setSpacing(16)
        
        # Categories title and manage button
        title_layout = QHBoxLayout()
        title_label = QLabel("Categories")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #1d1d1f;
        """)
        
        self.manage_categories_btn = QPushButton("⚙️")
        self.manage_categories_btn.setFixedSize(24, 24)
        self.manage_categories_btn.clicked.connect(self._manage_categories)
        self.manage_categories_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #dee2e6;
                border-radius: 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.manage_categories_btn)
        sidebar_layout.addLayout(title_layout)
        
        # Category list
        self.category_list = QListWidget()
        self.category_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                border: none;
                border-radius: 6px;
                padding: 10px 12px;
                margin: 1px 0;
                color: #495057;
                font-size: 13px;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
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
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)
        
        # Header with title and action buttons
        header_layout = QHBoxLayout()
        
        self.view_title = QLabel("All Entries")
        self.view_title.setStyleSheet("""
            font-size: 22px;
            font-weight: 600;
            color: #1d1d1f;
        """)
        
        # Action buttons
        self.add_entry_btn = QPushButton("+ Add Entry")
        self.add_entry_btn.clicked.connect(self._add_entry)
        self.add_entry_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        
        self.edit_entry_btn = QPushButton("Edit")
        self.edit_entry_btn.clicked.connect(self._edit_entry)
        self.edit_entry_btn.setEnabled(False)
        
        self.delete_entry_btn = QPushButton("Delete")
        self.delete_entry_btn.clicked.connect(self._delete_entry)
        self.delete_entry_btn.setEnabled(False)
        
        for btn in [self.edit_entry_btn, self.delete_entry_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #f8f9fa;
                }
                QPushButton:disabled {
                    color: #adb5bd;
                    border-color: #f1f3f5;
                }
            """)
        
        header_layout.addWidget(self.view_title)
        header_layout.addStretch()
        header_layout.addWidget(self.add_entry_btn)
        header_layout.addWidget(self.edit_entry_btn)
        header_layout.addWidget(self.delete_entry_btn)
        
        layout.addLayout(header_layout)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search your vault...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #adb5bd;
            }
        """)
        self.search_bar.textChanged.connect(self._filter_table)
        layout.addWidget(self.search_bar)
        
        self._setup_entries_table()
        layout.addWidget(self.table_widget)
        
        self.splitter.addWidget(content_widget)
        
        # Set splitter proportions
        self.splitter.setSizes([240, 600])
    
    def _setup_entries_table(self):
        """Setup the entries table."""
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Category", "Service", "Username", "Password", "URL"])
        
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
                font-size: 11px;
                color: #495057;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        
        # Configure table
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setShowGrid(False)
        
        # Context menu and interactions
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.table_widget.doubleClicked.connect(self._edit_entry)
        self.table_widget.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self):
        """Handle table selection changes."""
        has_selection = bool(self.table_widget.selectedItems())
        self.edit_entry_btn.setEnabled(has_selection)
        self.delete_entry_btn.setEnabled(has_selection)
    
    def _manage_categories(self):
        """Open category management dialog."""
        dialog = CategoryDialog(self.category_manager, self)
        dialog.categories_changed.connect(self._on_categories_changed)
        dialog.exec()
    
    def _on_categories_changed(self):
        """Handle category changes."""
        self._populate_category_list()
        self._filter_table()
        self.categories_changed.emit()
    
    def _populate_category_list(self):
        """Populate the category list."""
        self.category_list.clear()
        
        # Add "All Entries" item
        all_item = QListWidgetItem("📁 All Entries")
        all_item.setData(Qt.ItemDataRole.UserRole, None)
        self.category_list.addItem(all_item)
        
        # Add categories
        categories = self.category_manager.get_all_categories()
        for category in categories:
            display_text = f"{category.icon} {category.name}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, category.id)
            self.category_list.addItem(item)
        
        # Select "All Entries" by default
        self.category_list.setCurrentRow(0)
    
    def _on_category_filter_changed(self, item):
        """Handle category filter changes."""
        category_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_category_filter = category_id
        
        if category_id is None:
            self.view_title.setText("All Entries")
        else:
            category = self.category_manager.get_category(category_id)
            if category:
                self.view_title.setText(f"{category.icon} {category.name}")
        
        self._filter_table()
    
    def _add_entry(self):
        """Add a new entry."""
        dialog = EntryDialog(category_manager=self.category_manager, parent=self)
        dialog.entry_saved.connect(self._on_entry_saved)
        dialog.exec()
    
    def _edit_entry(self):
        """Edit selected entry."""
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        entry_data = self._get_entry_data_from_row(row)
        
        dialog = EntryDialog(entry_data=entry_data, category_manager=self.category_manager, parent=self)
        dialog.entry_saved.connect(lambda data: self._on_entry_updated(row, data))
        dialog.exec()
    
    def _delete_entry(self):
        """Delete selected entry."""
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        service = self.table_widget.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Delete Entry",
            f"Are you sure you want to delete the entry for '{service}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from filtered data and vault data
            if row < len(self.filtered_data):
                entry_to_remove = self.filtered_data[row]
                self.vault_data.remove(entry_to_remove)
                self._filter_table()
                self.data_changed.emit()
    
    def _on_entry_saved(self, entry_data):
        """Handle new entry saved."""
        self.vault_data.append(entry_data)
        self._filter_table()
        self.data_changed.emit()
    
    def _on_entry_updated(self, row, entry_data):
        """Handle entry updated."""
        if row < len(self.filtered_data):
            # Find the original entry in vault_data and update it
            old_entry = self.filtered_data[row]
            for i, entry in enumerate(self.vault_data):
                if entry == old_entry:
                    self.vault_data[i] = entry_data
                    break
        
        self._filter_table()
        self.data_changed.emit()
    
    def _get_entry_data_from_row(self, row):
        """Get entry data from table row."""
        if row < len(self.filtered_data):
            return self.filtered_data[row]
        return {}
    
    def _show_context_menu(self, position):
        """Show context menu for table items."""
        if not self.table_widget.itemAt(position):
            return
        
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 8px 16px;
                color: #495057;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #f8f9fa;
            }
        """)
        
        edit_action = menu.addAction("Edit Entry")
        edit_action.triggered.connect(self._edit_entry)
        
        menu.addSeparator()
        
        copy_user_action = menu.addAction("Copy Username")
        copy_user_action.triggered.connect(self._copy_username)
        
        copy_pass_action = menu.addAction("Copy Password")
        copy_pass_action.triggered.connect(self._copy_password)
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete Entry")
        delete_action.triggered.connect(self._delete_entry)
        
        menu.exec(self.table_widget.mapToGlobal(position))
    
    def _copy_username(self):
        """Copy username to clipboard."""
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            username = self.table_widget.item(row, 2).text()
            QApplication.clipboard().setText(username)
            self._start_clipboard_timer("Username copied to clipboard")
    
    def _copy_password(self):
        """Copy password to clipboard."""
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            if row < len(self.filtered_data):
                password = self.filtered_data[row].get("password", "")
                QApplication.clipboard().setText(password)
                self._start_clipboard_timer("Password copied to clipboard")
    
    def _start_clipboard_timer(self, message):
        """Start clipboard timer with status message."""
        # Emit status message to main window
        if hasattr(self.parent(), 'show_status_message'):
            self.parent().show_status_message(message)
        
        # Clear clipboard after 30 seconds for security
        self.clipboard_timer.start(30000)
    
    def _clear_clipboard(self):
        """Clear clipboard for security."""
        QApplication.clipboard().clear()
        if hasattr(self.parent(), 'show_status_message'):
            self.parent().show_status_message("Clipboard cleared for security")
    
    def _filter_table(self):
        """Filter table based on search and category."""
        search_text = self.search_bar.text().lower()
        
        # First filter by category
        if self.current_category_filter is None:
            # Show all entries
            category_filtered = self.vault_data
        else:
            # Filter by category
            category_filtered = [
                entry for entry in self.vault_data
                if entry.get("category", CategoryManager.UNCATEGORIZED_ID) == self.current_category_filter
            ]
        
        # Then filter by search text
        if search_text:
            self.filtered_data = [
                entry for entry in category_filtered
                if (search_text in entry.get("service", "").lower() or
                    search_text in entry.get("username", "").lower() or
                    search_text in entry.get("url", "").lower())
            ]
        else:
            self.filtered_data = category_filtered
        
        self._populate_table()
    
    def _populate_table(self):
        """Populate the table with filtered data."""
        self.table_widget.setRowCount(len(self.filtered_data))
        
        for row, entry in enumerate(self.filtered_data):
            # Category
            category_id = entry.get("category", CategoryManager.UNCATEGORIZED_ID)
            category = self.category_manager.get_category(category_id)
            category_text = f"{category.icon} {category.name}" if category else "Uncategorized"
            self.table_widget.setItem(row, 0, QTableWidgetItem(category_text))
            
            # Service
            self.table_widget.setItem(row, 1, QTableWidgetItem(entry.get("service", "")))
            
            # Username
            self.table_widget.setItem(row, 2, QTableWidgetItem(entry.get("username", "")))
            
            # Password (masked)
            password_item = QTableWidgetItem("••••••••")
            self.table_widget.setItem(row, 3, password_item)
            
            # URL
            self.table_widget.setItem(row, 4, QTableWidgetItem(entry.get("url", "")))
    
    def set_vault_data(self, data):
        """Set vault data."""
        self.vault_data = data
        # Initialize with "All Entries" filter (current_category_filter = None)
        self.current_category_filter = None
        # Trigger the filter to properly populate the table
        self._filter_table()
    
    def get_vault_data(self):
        """Get vault data."""
        return self.vault_data


class SettingsTab(QWidget):
    """Tab containing application settings and preferences."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the settings tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: 600;
            color: #1d1d1f;
            padding: 10px 0;
        """)
        layout.addWidget(title)
        
        # Security Settings
        security_group = QGroupBox("Security")
        security_group.setStyleSheet(self._get_group_style())
        security_layout = QFormLayout(security_group)
        
        self.auto_lock_spin = QSpinBox()
        self.auto_lock_spin.setMinimum(1)
        self.auto_lock_spin.setMaximum(60)
        self.auto_lock_spin.setValue(5)
        self.auto_lock_spin.setSuffix(" minutes")
        security_layout.addRow("Auto-lock timeout:", self.auto_lock_spin)
        
        self.clipboard_timeout_spin = QSpinBox()
        self.clipboard_timeout_spin.setMinimum(10)
        self.clipboard_timeout_spin.setMaximum(300)
        self.clipboard_timeout_spin.setValue(30)
        self.clipboard_timeout_spin.setSuffix(" seconds")
        security_layout.addRow("Clipboard timeout:", self.clipboard_timeout_spin)
        
        layout.addWidget(security_group)
        
        # Appearance Settings
        appearance_group = QGroupBox("Appearance")
        appearance_group.setStyleSheet(self._get_group_style())
        appearance_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(appearance_group)
        
        # Vault Settings
        vault_group = QGroupBox("Vault")
        vault_group.setStyleSheet(self._get_group_style())
        vault_layout = QVBoxLayout(vault_group)
        
        # Vault location
        location_layout = QHBoxLayout()
        self.vault_location_input = QLineEdit()
        self.vault_location_input.setPlaceholderText("~/.config/pyvault/vault.dat")
        self.vault_location_input.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_vault_location)
        
        location_layout.addWidget(self.vault_location_input)
        location_layout.addWidget(browse_btn)
        vault_layout.addLayout(location_layout)
        
        # Backup options
        backup_btn = QPushButton("Create Backup")
        backup_btn.clicked.connect(self._create_backup)
        vault_layout.addWidget(backup_btn)
        
        layout.addWidget(vault_group)
        
        # About Section
        about_group = QGroupBox("About")
        about_group.setStyleSheet(self._get_group_style())
        about_layout = QVBoxLayout(about_group)
        
        about_text = QLabel("""
        <b>PyVault</b><br>
        Version 1.0.0<br><br>
        A secure desktop password manager built with Python and PySide6.<br>
        Uses AES-256-GCM encryption to keep your passwords safe.
        """)
        about_text.setWordWrap(True)
        about_text.setStyleSheet("color: #495057; line-height: 1.4;")
        about_layout.addWidget(about_text)
        
        layout.addWidget(about_group)
        
        layout.addStretch()
    
    def _browse_vault_location(self):
        """Browse for vault file location."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Vault Location",
            "",
            "PyVault Files (*.dat);;All Files (*)"
        )
        if file_path:
            self.vault_location_input.setText(file_path)
    
    def _create_backup(self):
        """Create a backup of the vault."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Create Vault Backup",
            "",
            "PyVault Backup Files (*.dat);;All Files (*)"
        )
        if file_path:
            # TODO: Implement backup functionality
            QMessageBox.information(self, "Backup", f"Backup saved to {file_path}")
    
    def _get_group_style(self):
        """Get group box style."""
        return """
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #1d1d1f;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding-top: 10px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """


class TabbedMainWindow(QMainWindow):
    """Modern tab-based main window for PyVault."""
    
    data_changed = Signal()
    lock_requested = Signal()
    
    def __init__(self, category_manager=None):
        super().__init__()
        self.setWindowTitle("PyVault - Your Personal Vault")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self.category_manager = category_manager or CategoryManager()
        
        self._setup_ui()
        self._setup_menubar()
        self._setup_statusbar()
    
    def _setup_ui(self):
        """Setup the main UI."""
        # Central widget with tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 2px solid transparent;
                padding: 12px 24px;
                margin: 0;
                font-weight: 500;
                font-size: 14px;
                color: #495057;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #f8f9fa;
                color: #2196f3;
                border-bottom: 2px solid #2196f3;
            }
            QTabBar::tab:hover {
                color: #1976d2;
            }
        """)
        
        # Create tabs
        self.vault_tab = VaultTab(self.category_manager)
        self.vault_tab.data_changed.connect(self.data_changed)
        self.vault_tab.categories_changed.connect(self._update_status)
        
        self.generator_tab = PasswordGeneratorWidget()
        self.settings_tab = SettingsTab()
        
        # Add tabs
        self.tab_widget.addTab(self.vault_tab, "🔐 Vault")
        self.tab_widget.addTab(self.generator_tab, "🔑 Generator")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        
        layout.addWidget(self.tab_widget)
        
        # Connect signals
        self.vault_tab.data_changed.connect(self._update_status)
    
    def _setup_menubar(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Entry", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._switch_to_vault_and_add)
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
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        generator_action = QAction("Password &Generator", self)
        generator_action.setShortcut(QKeySequence("Ctrl+G"))
        generator_action.triggered.connect(self._switch_to_generator)
        tools_menu.addAction(generator_action)
        
        categories_action = QAction("Manage &Categories", self)
        categories_action.setShortcut(QKeySequence("Ctrl+T"))
        categories_action.triggered.connect(self.vault_tab._manage_categories)
        tools_menu.addAction(categories_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About PyVault", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_statusbar(self):
        """Setup the status bar."""
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
        self._update_status()
    
    def _switch_to_vault_and_add(self):
        """Switch to vault tab and add new entry."""
        self.tab_widget.setCurrentIndex(0)
        self.vault_tab._add_entry()
    
    def _switch_to_generator(self):
        """Switch to generator tab."""
        self.tab_widget.setCurrentIndex(1)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About PyVault",
            """
            <h3>PyVault</h3>
            <p>Version 1.0.0</p>
            <p>A secure desktop password manager built with Python and PySide6.</p>
            <p>Your passwords are encrypted using AES-256-GCM encryption and stored locally on your device.</p>
            """
        )
    
    def _update_status(self):
        """Update status bar."""
        entry_count = len(self.vault_tab.vault_data)
        category_count = len(self.category_manager.get_all_categories()) - 1  # Exclude "Uncategorized"
        
        if entry_count == 0:
            status_text = "No entries"
        elif entry_count == 1:
            status_text = "1 entry"
        else:
            status_text = f"{entry_count} entries"
        
        if category_count > 0:
            status_text += f" • {category_count} categories"
        
        status_text += " • Vault unlocked"
        self.statusbar.showMessage(status_text)
    
    def show_status_message(self, message, timeout=3000):
        """Show a temporary status message."""
        self.statusbar.showMessage(message, timeout)
        QTimer.singleShot(timeout, self._update_status)
    
    def set_vault_data(self, data):
        """Set vault data."""
        self.vault_tab.set_vault_data(data)
        self._update_status()
    
    def get_vault_data(self):
        """Get vault data."""
        return self.vault_tab.get_vault_data()
