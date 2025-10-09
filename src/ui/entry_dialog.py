"""
PyVault Entry Dialog - V2 (Bitwarden Inspired)
A redesigned modal for adding and editing vault entries.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFormLayout, QTextEdit, QComboBox, QWidget
)
from PySide6.QtCore import Qt, Signal, Slot

from .design_system import tokens, get_global_stylesheet
from ..category_manager import CategoryManager

class EntryDialog(QDialog):
    """A clean, dark-themed dialog for managing entries."""

    def __init__(self, parent=None, entry_data=None, category_manager=None):
        super().__init__(parent)
        self.entry_data = entry_data or {}
        self.is_edit_mode = bool(entry_data)
        self.category_manager = category_manager

        self.setWindowTitle("Add Item" if not self.is_edit_mode else "Edit Item")
        self.setModal(True)
        self.setMinimumWidth(450)

        self._setup_ui()
        self.setStyleSheet(get_global_stylesheet())

        if self.is_edit_mode:
            self._load_data()

    def _setup_ui(self):
        """Sets up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(tokens.spacing.lg)
        layout.setContentsMargins(tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg)

        title = QLabel("Add Item" if not self.is_edit_mode else "Edit Item")
        title.setStyleSheet(f"font-size: {tokens.typography.text_xl}pt; font-weight: {tokens.typography.font_semibold};")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(tokens.spacing.md)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.service_input = QLineEdit()
        self.username_input = QLineEdit()

        # --- Password Field with Show/Hide Button ---
        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(tokens.spacing.xs)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_input)

        self.show_hide_button = QPushButton("Show")
        self.show_hide_button.setCheckable(True)
        self.show_hide_button.toggled.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.show_hide_button)
        # --- End Password Field ---

        self.url_input = QLineEdit()
        self.category_combo = QComboBox()
        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(80)

        self._populate_category_combo()

        form_layout.addRow("Service:", self.service_input)
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", password_container)
        form_layout.addRow("URL:", self.url_input)
        form_layout.addRow("Category:", self.category_combo)
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    @Slot(bool)
    def _toggle_password_visibility(self, checked):
        """Toggles the visibility of the password field."""
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_hide_button.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_hide_button.setText("Show")

    def _load_data(self):
        """Loads existing entry data into the form."""
        self.service_input.setText(self.entry_data.get("service", ""))
        self.username_input.setText(self.entry_data.get("username", ""))
        self.password_input.setText(self.entry_data.get("password", ""))
        self.url_input.setText(self.entry_data.get("url", ""))
        self.notes_input.setPlainText(self.entry_data.get("notes", ""))
        
        if self.category_manager:
            category_id = self.entry_data.get("category", CategoryManager.UNCATEGORIZED_ID)
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == category_id:
                    self.category_combo.setCurrentIndex(i)
                    break

    def get_entry_data(self) -> dict:
        """Returns the data entered in the form."""
        return {
            "service": self.service_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "url": self.url_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip(),
            "category": self.category_combo.currentData() or CategoryManager.UNCATEGORIZED_ID
        }

    def _populate_category_combo(self):
        """Populates the category dropdown."""
        if not self.category_manager: return
        for category in self.category_manager.get_all_categories():
            self.category_combo.addItem(f"{category.icon} {category.name}", category.id)
