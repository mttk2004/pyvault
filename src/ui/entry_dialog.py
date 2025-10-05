from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFormLayout, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal

from ..category_manager import CategoryManager, Category

class EntryDialog(QDialog):
    """Dialog for adding or editing vault entries."""

    entry_saved = Signal(dict)  # Emits the entry data when saved

    def __init__(self, parent=None, entry_data=None, category_manager=None):
        super().__init__(parent)
        self.entry_data = entry_data or {}
        self.is_edit_mode = bool(entry_data)
        self.category_manager = category_manager

        self.setWindowTitle("Edit Entry" if self.is_edit_mode else "Add New Entry")
        self.setModal(True)
        self.setMinimumWidth(500)

        self._setup_ui()

        if self.is_edit_mode:
            self._load_data()

    def _setup_ui(self):
        """Sets up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(32, 32, 32, 32)

        # Title - simple and clean
        title = QLabel("Edit Entry" if self.is_edit_mode else "Add New Entry")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 500;
            color: #1d1d1f;
            padding-bottom: 4px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("All fields are required except notes")
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #86868b;
            padding-bottom: 16px;
        """)
        layout.addWidget(subtitle)

        # Form - cleaner spacing
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Service name
        service_label = QLabel("Service")
        service_label.setStyleSheet("font-weight: 500; color: #1d1d1f;")
        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("Google, GitHub, etc.")
        form_layout.addRow(service_label, self.service_input)

        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-weight: 500; color: #1d1d1f;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("user@example.com")
        form_layout.addRow(username_label, self.username_input)

        # Password - simplified
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: 500; color: #1d1d1f;")
        password_layout = QHBoxLayout()
        password_layout.setSpacing(8)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")

        self.show_password_btn = QPushButton("Show")
        self.show_password_btn.setFixedWidth(60)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self._toggle_password_visibility)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                padding: 8px;
                color: #1d1d1f;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f5f5f7;
            }
            QPushButton:checked {
                background-color: #e8e8ed;
                border-color: #86868b;
            }
        """)

        self.generate_password_btn = QPushButton("Generate")
        self.generate_password_btn.setFixedWidth(90)
        self.generate_password_btn.clicked.connect(self._generate_password)
        self.generate_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                padding: 8px;
                color: #1d1d1f;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f5f5f7;
            }
        """)

        password_layout.addWidget(self.password_input, 1)
        password_layout.addWidget(self.show_password_btn)
        password_layout.addWidget(self.generate_password_btn)

        form_layout.addRow(password_label, password_layout)

        # URL
        url_label = QLabel("URL")
        url_label.setStyleSheet("font-weight: 500; color: #1d1d1f;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        form_layout.addRow(url_label, self.url_input)

        # Category
        if self.category_manager:
            category_label = QLabel("Category")
            category_label.setStyleSheet("font-weight: 500; color: #1d1d1f;")
            self.category_combo = QComboBox()
            self.category_combo.setStyleSheet("""
                QComboBox {
                    border: 1px solid #d1d1d6;
                    border-radius: 6px;
                    padding: 8px 12px;
                    background-color: white;
                    font-size: 13px;
                    color: #1d1d1f;
                    min-width: 200px;
                }
                QComboBox:hover {
                    border-color: #adb5bd;
                }
                QComboBox:focus {
                    border-color: #667eea;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 25px;
                    border-left-width: 1px;
                    border-left-color: #d1d1d6;
                    border-left-style: solid;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    background-color: #f5f5f7;
                }
                QComboBox::down-arrow {
                    width: 8px;
                    height: 8px;
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #d1d1d6;
                    border-radius: 6px;
                    background-color: white;
                    selection-background-color: #e3f2fd;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    padding: 8px 12px;
                    border-bottom: 1px solid #f1f3f5;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #e3f2fd;
                    color: #1565c0;
                }
            """)
            self._populate_category_combo()
            form_layout.addRow(category_label, self.category_combo)
        else:
            self.category_combo = None

        # Notes (optional) - more compact
        notes_label = QLabel("Notes (optional)")
        notes_label.setStyleSheet("font-weight: 500; color: #86868b;")
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add any additional notes here...")
        self.notes_input.setMaximumHeight(70)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                padding: 8px;
                background-color: #f5f5f7;
            }
            QTextEdit:focus {
                background-color: white;
                border-color: #667eea;
            }
        """)
        form_layout.addRow(notes_label, self.notes_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Buttons - cleaner design
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #d1d1d6;
                border-radius: 8px;
                padding: 0 24px;
                color: #1d1d1f;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f5f5f7;
            }
        """)

        self.save_btn = QPushButton("Save" if self.is_edit_mode else "Add Entry")
        self.save_btn.setFixedHeight(40)
        self.save_btn.clicked.connect(self._save_entry)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d1d1f;
                border: none;
                border-radius: 8px;
                padding: 0 24px;
                color: white;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2d2d2f;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _load_data(self):
        """Loads existing entry data into the form."""
        self.service_input.setText(self.entry_data.get("service", ""))
        self.username_input.setText(self.entry_data.get("username", ""))
        self.password_input.setText(self.entry_data.get("password", ""))
        self.url_input.setText(self.entry_data.get("url", ""))
        self.notes_input.setPlainText(self.entry_data.get("notes", ""))
        
        # Load category if available
        if self.category_combo and self.category_manager:
            category_id = self.entry_data.get("category", CategoryManager.UNCATEGORIZED_ID)
            self._select_category_in_combo(category_id)

    def _toggle_password_visibility(self, checked):
        """Toggles password visibility."""
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def _generate_password(self):
        """Generates a random strong password."""
        import string
        import secrets

        # Generate a 16-character password with mixed characters
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(16))

        self.password_input.setText(password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.show_password_btn.setChecked(True)

    def _save_entry(self):
        """Validates and saves the entry."""
        service = self.service_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        url = self.url_input.text().strip()
        notes = self.notes_input.toPlainText().strip()

        if not service:
            self.service_input.setFocus()
            return

        if not username:
            self.username_input.setFocus()
            return

        if not password:
            self.password_input.setFocus()
            return

        entry = {
            "service": service,
            "username": username,
            "password": password,
            "url": url,
            "notes": notes
        }
        
        # Add category if available
        if self.category_combo and self.category_manager:
            selected_category_id = self._get_selected_category_id()
            if selected_category_id:
                entry["category"] = selected_category_id
            else:
                entry["category"] = CategoryManager.UNCATEGORIZED_ID

        self.entry_saved.emit(entry)
        self.accept()
    
    def _populate_category_combo(self):
        """Populate the category combo box."""
        if not self.category_manager:
            return
        
        self.category_combo.clear()
        
        categories = self.category_manager.get_all_categories()
        for category in categories:
            # Create display text with icon and name
            display_text = f"{category.icon} {category.name}"
            
            # Add item with category ID as data
            self.category_combo.addItem(display_text, category.id)
            
            # Set color for the item (create colored circle)
            item_index = self.category_combo.count() - 1
            # Note: We could add a colored indicator here if needed
    
    def _select_category_in_combo(self, category_id: str):
        """Select a category in the combo box by ID."""
        if not self.category_combo:
            return
        
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == category_id:
                self.category_combo.setCurrentIndex(i)
                break
    
    def _get_selected_category_id(self) -> str:
        """Get the selected category ID from the combo box."""
        if not self.category_combo:
            return CategoryManager.UNCATEGORIZED_ID
        
        current_index = self.category_combo.currentIndex()
        if current_index >= 0:
            return self.category_combo.itemData(current_index)
        
        return CategoryManager.UNCATEGORIZED_ID
