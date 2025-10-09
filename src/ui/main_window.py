"""
PyVault Main Window - V2 (Bitwarden Inspired)
A complete rewrite featuring a three-panel dark-themed layout.
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QPushButton, QHeaderView, QAbstractItemView,
    QLineEdit, QToolBar, QStatusBar, QSplitter, QListWidget,
    QListWidgetItem, QLabel, QFrame, QFormLayout, QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtGui import QIcon, QAction

from .design_system import tokens, get_global_stylesheet
from .entry_dialog import EntryDialog
from .category_dialog import CategoryDialog
from .toast_notification import show_success_toast, show_warning_toast
from ..category_manager import CategoryManager
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
        self._update_detail_view(None) # Start with empty detail view

    def _setup_ui(self):
        """Setup the main UI components."""
        # --- Toolbar ---
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        add_action = QAction(QIcon("src/assets/icons/plus-circle.svg"), "Add Entry", self)
        add_action.triggered.connect(self._add_entry)
        toolbar.addAction(add_action)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search vault...")
        self.search_bar.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_bar)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        lock_action = QAction(QIcon("src/assets/icons/lock.svg"), "Lock Vault", self)
        lock_action.triggered.connect(self.lock_requested)
        toolbar.addAction(lock_action)

        # --- Central Widget (Splitter) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        self.splitter.addWidget(self._create_left_panel())
        self.splitter.addWidget(self._create_middle_panel())
        self.splitter.addWidget(self._create_right_panel())
        
        self.splitter.setSizes([200, 300, 400]) # Initial sizes for panels
        self.splitter.setStretchFactor(1, 1) # Allow middle panel to stretch

    def _create_left_panel(self) -> QWidget:
        """Creates the left panel for categories."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(tokens.spacing.sm, tokens.spacing.md, tokens.spacing.sm, tokens.spacing.md)
        layout.setSpacing(tokens.spacing.md)

        title = QLabel("Categories")
        title.setStyleSheet(f"font-size: {tokens.typography.text_lg}pt; font-weight: {tokens.typography.font_semibold};")
        
        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self._on_category_filter_changed)
        
        layout.addWidget(title)
        layout.addWidget(self.category_list)
        return panel

    def _create_middle_panel(self) -> QWidget:
        """Creates the middle panel for the entry list."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(tokens.spacing.sm, tokens.spacing.md, tokens.spacing.sm, tokens.spacing.md)
        
        self.table_view = QTableView()
        self.table_model = EntryTableModel(headers=["Service", "Username"], category_manager=self.category_manager)
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_view.verticalHeader().hide()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.table_view)
        return panel

    def _create_right_panel(self) -> QWidget:
        """Creates the right panel for entry details."""
        self.detail_panel = QWidget()
        layout = QVBoxLayout(self.detail_panel)
        layout.setContentsMargins(tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg)
        
        # --- Header ---
        header_layout = QHBoxLayout()
        self.detail_title = QLabel("Select an item")
        self.detail_title.setStyleSheet(f"font-size: {tokens.typography.text_xl}pt; font-weight: {tokens.typography.font_bold};")
        header_layout.addWidget(self.detail_title)
        header_layout.addStretch()
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self._edit_entry)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self._delete_entry)
        header_layout.addWidget(self.edit_button)
        header_layout.addWidget(self.delete_button)
        layout.addLayout(header_layout)

        # --- Form ---
        self.detail_form = QFrame()
        self.detail_form.setObjectName("detailForm")
        self.detail_form.setStyleSheet(f"QFrame#detailForm {{ border-top: 1px solid {tokens.colors.border_primary}; margin-top: {tokens.spacing.md}px; }}")
        form_layout = QFormLayout(self.detail_form)
        form_layout.setSpacing(tokens.spacing.md)
        
        self.detail_username = self._create_detail_row("Username")
        self.detail_password = self._create_detail_row("Password", is_password=True)
        self.detail_url = self._create_detail_row("URL")
        self.detail_notes = self._create_detail_row("Notes")
        
        form_layout.addRow(self.detail_username["label"], self.detail_username["widget"])
        form_layout.addRow(self.detail_password["label"], self.detail_password["widget"])
        form_layout.addRow(self.detail_url["label"], self.detail_url["widget"])
        form_layout.addRow(self.detail_notes["label"], self.detail_notes["widget"])
        
        layout.addWidget(self.detail_form)
        layout.addStretch()
        return self.detail_panel

    def _create_detail_row(self, label_text, is_password=False) -> dict:
        """Helper to create a row in the detail panel."""
        label = QLabel(label_text)
        value_widget = QLineEdit()
        value_widget.setReadOnly(True)
        
        layout = QHBoxLayout()
        layout.addWidget(value_widget)
        copy_button = QPushButton("Copy")
        copy_button.setFixedWidth(60)
        layout.addWidget(copy_button)
        
        if is_password:
            value_widget.setEchoMode(QLineEdit.EchoMode.Password)
            show_button = QPushButton("Show")
            show_button.setCheckable(True)
            show_button.setFixedWidth(60)
            show_button.toggled.connect(lambda checked, w=value_widget: w.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password))
            layout.addWidget(show_button)

        container = QWidget()
        container.setLayout(layout)
        
        return {"label": label, "widget": container, "value": value_widget, "copy": copy_button}

    @Slot()
    def _on_selection_changed(self):
        """Update the detail view when the table selection changes."""
        indexes = self.table_view.selectionModel().selectedRows()
        if indexes:
            entry = self.table_model.get_entry(indexes[0].row())
            self._update_detail_view(entry)
        else:
            self._update_detail_view(None)

    def _update_detail_view(self, entry: dict | None):
        """Populate the right panel with entry details."""
        if entry:
            self.detail_title.setText(entry.get("service", "Details"))
            self.detail_username["value"].setText(entry.get("username", ""))
            self.detail_password["value"].setText(entry.get("password", ""))
            self.detail_url["value"].setText(entry.get("url", ""))
            self.detail_notes["value"].setText(entry.get("notes", ""))

            # Connect copy buttons
            self.detail_username["copy"].clicked.connect(lambda: self._copy_to_clipboard(self.detail_username["value"].text(), "Username"))
            self.detail_password["copy"].clicked.connect(lambda: self._copy_to_clipboard(self.detail_password["value"].text(), "Password"))
            self.detail_url["copy"].clicked.connect(lambda: self._copy_to_clipboard(self.detail_url["value"].text(), "URL"))

            self.detail_form.show()
            self.edit_button.show()
            self.delete_button.show()
        else:
            self.detail_title.setText("Select an item")
            self.detail_form.hide()
            self.edit_button.hide()
            self.delete_button.hide()

    def populate_data(self, data: list[dict]):
        self.vault_data = data
        self._refresh_ui()

    def _refresh_ui(self):
        self._populate_category_sidebar()
        self._apply_current_filter()

    def _populate_category_sidebar(self):
        self.category_list.clear()
        counts = self.category_manager.count_entries_by_category(self.vault_data)
        
        all_item = QListWidgetItem(f"All Items ({len(self.vault_data)})")
        all_item.setData(Qt.ItemDataRole.UserRole, "ALL")
        self.category_list.addItem(all_item)

        for cat in self.category_manager.get_all_categories():
            item = QListWidgetItem(f"{cat.icon} {cat.name} ({counts.get(cat.id, 0)})")
            item.setData(Qt.ItemDataRole.UserRole, cat.id)
            self.category_list.addItem(item)
        
        # Reselect current filter
        for i in range(self.category_list.count()):
            if self.category_list.item(i).data(Qt.ItemDataRole.UserRole) == self.current_category_filter:
                self.category_list.setCurrentRow(i)
                break

    @Slot()
    def _on_category_filter_changed(self, item: QListWidgetItem):
        self.current_category_filter = item.data(Qt.ItemDataRole.UserRole)
        self._apply_current_filter()

    def _apply_current_filter(self):
        search_text = self.search_bar.text().lower()
        
        if self.current_category_filter == "ALL":
            self.filtered_data = self.vault_data
        else:
            self.filtered_data = [
                e for e in self.vault_data
                if e.get("category", CategoryManager.UNCATEGORIZED_ID) == self.current_category_filter
            ]

        if search_text:
            self.filtered_data = [
                e for e in self.filtered_data
                if search_text in e.get("service", "").lower() or search_text in e.get("username", "").lower()
            ]

        self.table_model.set_data(self.filtered_data)
        self._update_detail_view(None)

    @Slot()
    def _filter_table(self):
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
    def _edit_entry(self):
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            show_warning_toast("Select an item to edit.", parent=self)
            return

        selected_entry = self.table_model.get_entry(indexes[0].row())
        dialog = EntryDialog(self, entry_data=selected_entry, category_manager=self.category_manager)
        if dialog.exec():
            updated_data = dialog.get_entry_data()
            # Find and update original entry
            for i, entry in enumerate(self.vault_data):
                if entry is selected_entry:
                    self.vault_data[i] = updated_data
                    break
            self.data_changed.emit()
            self._refresh_ui()

    @Slot()
    def _delete_entry(self):
        # Implementation for deleting entry
        pass

    def _copy_to_clipboard(self, text: str, item_name: str):
        QApplication.clipboard().setText(text)
        show_success_toast(f"{item_name} copied to clipboard.", parent=self)
