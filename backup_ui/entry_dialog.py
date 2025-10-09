"""
PyVault Entry Dialog - V2 (Bitwarden Inspired)
A redesigned modal for adding and editing vault entries.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFormLayout, QTextEdit, QComboBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from .design_system import tokens

from .design_system import tokens, get_global_stylesheet
from ..category_manager import CategoryManager

class PasswordStrengthBar(QProgressBar):
    """Custom password strength indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(4)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {tokens.colors.surface_secondary};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {tokens.colors.error};
                border-radius: 2px;
            }}
        """)

    def set_strength(self, strength: int):
        """Set password strength (0-5)"""
        self.setValue(strength)
        self.setMaximum(5)

        if strength <= 2:
            color = tokens.colors.error
        elif strength <= 4:
            color = tokens.colors.warning
        else:
            color = tokens.colors.success

        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {tokens.colors.surface_secondary};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)

class EntryDialog(QDialog):
    """Dialog for adding or editing vault entries."""

    entry_saved = Signal(dict)

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

        title = QLabel("Edit Entry" if self.is_edit_mode else "Add New Entry")
        title.setStyleSheet(f"""
            font-size: {tokens.typography.text_2xl}px;
            font-weight: {tokens.typography.font_semibold};
            color: {tokens.colors.text_primary};
            padding-bottom: 4px;
        """)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(tokens.spacing.md)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("e.g., Google, GitHub")
        form_layout.addRow(QLabel("Service"), self.service_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g., user@example.com")
        form_layout.addRow(QLabel("Username"), self.username_input)

        password_layout = QVBoxLayout()
        password_hbox = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.textChanged.connect(self._update_password_strength)

        self.show_password_btn = QPushButton("Show")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self._toggle_password_visibility)

        self.generate_password_btn = QPushButton("Generate")
        self.generate_password_btn.clicked.connect(self._generate_password)

        password_hbox.addWidget(self.password_input)
        password_hbox.addWidget(self.show_password_btn)
        password_hbox.addWidget(self.generate_password_btn)

        self.strength_bar = PasswordStrengthBar()
        self.strength_label = QLabel("")

        password_layout.addLayout(password_hbox)
        password_layout.addWidget(self.strength_bar)
        password_layout.addWidget(self.strength_label)

        form_layout.addRow(QLabel("Password"), password_layout)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g., https://example.com")
        form_layout.addRow(QLabel("URL"), self.url_input)

        if self.category_manager:
            self.category_combo = QComboBox()
            self._populate_category_combo()
            form_layout.addRow(QLabel("Category"), self.category_combo)
        else:
            self.category_combo = None

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add any additional notes...")
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow(QLabel("Notes"), self.notes_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_entry)
        self.save_btn.setObjectName("primaryButton")
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)

        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {tokens.colors.surface};
            }}
            QLabel {{
                font-size: {tokens.typography.text_sm}px;
                color: {tokens.colors.text_secondary};
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {tokens.colors.input_background};
                border: 1px solid {tokens.colors.input_border};
                border-radius: {tokens.border_radius.md}px;
                padding: {tokens.spacing.sm}px {tokens.spacing.md}px;
                font-size: {tokens.typography.text_sm}px;
                color: {tokens.colors.text_primary};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border-color: {tokens.colors.primary};
            }}
            QPushButton {{
                padding: {tokens.spacing.sm}px {tokens.spacing.lg}px;
                border-radius: {tokens.border_radius.md}px;
                font-size: {tokens.typography.text_sm}px;
                font-weight: {tokens.typography.font_medium};
            }}
            QPushButton#primaryButton {{
                background-color: {tokens.colors.primary};
                color: {tokens.colors.text_inverse};
                border: none;
            }}
            QPushButton#primaryButton:hover {{
                background-color: {tokens.colors.primary_dark};
            }}
        """)
        self.strength_label.setStyleSheet(f"font-size: {tokens.typography.text_xs}px; color: {tokens.colors.text_tertiary};")

    def _load_data(self):
        """Loads existing entry data into the form."""
        self.service_input.setText(self.entry_data.get("service", ""))
        self.username_input.setText(self.entry_data.get("username", ""))
        self.password_input.setText(self.entry_data.get("password", ""))
        self.url_input.setText(self.entry_data.get("url", ""))
        self.notes_input.setPlainText(self.entry_data.get("notes", ""))
        
        if self.category_combo and self.category_manager:
            category_id = self.entry_data.get("category", CategoryManager.UNCATEGORIZED_ID)
            self._select_category_in_combo(category_id)

        self._update_password_strength()

    def _toggle_password_visibility(self, checked):
        """Toggles password visibility."""
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("Show")

    def _generate_password(self):
        """Opens the advanced password generator dialog."""
        from .password_generator_dialog import PasswordGeneratorDialog
        
        dialog = PasswordGeneratorDialog(self)
        dialog.password_generated.connect(self._use_generated_password)
        dialog.exec()
    
    def _use_generated_password(self, password: str):
        """Use the password from the generator dialog."""
        self.password_input.setText(password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.show_password_btn.setChecked(True)

    def _update_password_strength(self):
        """Update password strength indicator."""
        password = self.password_input.text()
        if not password:
            self.strength_bar.hide()
            self.strength_label.setText("")
            return

        self.strength_bar.show()
        strength = 0
        feedback = []

        if len(password) >= 8: strength += 1
        else: feedback.append("8+ chars")

        if any(c.isupper() for c in password): strength += 1
        else: feedback.append("uppercase")

        if any(c.islower() for c in password): strength += 1
        else: feedback.append("lowercase")

        if any(c.isdigit() for c in password): strength += 1
        else: feedback.append("number")

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~`" for c in password): strength += 1
        else: feedback.append("special")

        self.strength_bar.set_strength(strength)

        if strength <= 2:
            self.strength_label.setText(f"Weak. Add: {', '.join(feedback)}")
            self.strength_label.setStyleSheet(f"color: {tokens.colors.error};")
        elif strength <= 4:
            self.strength_label.setText(f"Medium. Consider: {', '.join(feedback)}")
            self.strength_label.setStyleSheet(f"color: {tokens.colors.warning};")
        else:
            self.strength_label.setText("Strong password")
            self.strength_label.setStyleSheet(f"color: {tokens.colors.success};")

    def _save_entry(self):
        """Validates and saves the entry."""
        service = self.service_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        url = self.url_input.text().strip()
        notes = self.notes_input.toPlainText().strip()

        if not service or not username or not password:
            # Basic validation feedback
            return

        entry = {
            "service": service, "username": username, "password": password,
            "url": url, "notes": notes
        }
        
        if self.category_combo and self.category_manager:
            entry["category"] = self._get_selected_category_id()

    def _populate_category_combo(self):
        """Populate the category combo box."""
        if not self.category_manager: return
        self.category_combo.clear()
        for category in self.category_manager.get_all_categories():
            self.category_combo.addItem(f"{category.icon} {category.name}", category.id)
    
    def _select_category_in_combo(self, category_id: str):
        """Select a category in the combo box by ID."""
        if not self.category_combo: return
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == category_id:
                self.category_combo.setCurrentIndex(i)
                break
    
    def _get_selected_category_id(self) -> str:
        """Get the selected category ID from the combo box."""
        if not self.category_combo: return CategoryManager.UNCATEGORIZED_ID
        return self.category_combo.currentData() or CategoryManager.UNCATEGORIZED_ID
