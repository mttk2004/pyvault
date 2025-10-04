from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFormLayout, QTextEdit
)
from PySide6.QtCore import Qt, Signal

class EntryDialog(QDialog):
    """Dialog for adding or editing vault entries."""
    
    entry_saved = Signal(dict)  # Emits the entry data when saved
    
    def __init__(self, parent=None, entry_data=None):
        super().__init__(parent)
        self.entry_data = entry_data or {}
        self.is_edit_mode = bool(entry_data)
        
        self.setWindowTitle("Edit Entry" if self.is_edit_mode else "Add New Entry")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self._setup_ui()
        
        if self.is_edit_mode:
            self._load_data()
    
    def _setup_ui(self):
        """Sets up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("✏️ Edit Entry" if self.is_edit_mode else "➕ Add New Entry")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #1d1d1f;
            padding-bottom: 8px;
        """)
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Service name
        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("e.g., Google, GitHub, Facebook")
        form_layout.addRow("Service Name:", self.service_input)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g., user@example.com")
        form_layout.addRow("Username:", self.username_input)
        
        # Password
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedWidth(40)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self._toggle_password_visibility)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f7;
                border: 1px solid #d1d1d6;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:checked {
                background-color: #667eea;
                color: white;
            }
        """)
        
        self.generate_password_btn = QPushButton("🎲 Generate")
        self.generate_password_btn.clicked.connect(self._generate_password)
        self.generate_password_btn.setObjectName("SecondaryButton")
        
        password_layout.addWidget(self.password_input, 1)
        password_layout.addWidget(self.show_password_btn)
        password_layout.addWidget(self.generate_password_btn)
        
        form_layout.addRow("Password:", password_layout)
        
        # URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g., https://example.com")
        form_layout.addRow("URL:", self.url_input)
        
        # Notes (optional)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        self.notes_input.setMaximumHeight(80)
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("SecondaryButton")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("💾 Save" if self.is_edit_mode else "✨ Add Entry")
        self.save_btn.clicked.connect(self._save_entry)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
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
        
        self.entry_saved.emit(entry)
        self.accept()
