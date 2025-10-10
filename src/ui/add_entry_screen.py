from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QDialogButtonBox
from src.ui.password_generator_screen import PasswordGeneratorScreen

class AddEntryScreen(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Entry")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        # Form fields
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        self.layout.addWidget(self.title_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input)

        # Password field with a generate button
        self.password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.generate_password_button = QPushButton("Generate")
        self.generate_password_button.clicked.connect(self.open_password_generator) # Connect the button
        self.password_layout.addWidget(self.password_input)
        self.password_layout.addWidget(self.generate_password_button)
        self.layout.addLayout(self.password_layout)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL")
        self.layout.addWidget(self.url_input)

        # Category dropdown
        self.category_combo = QComboBox()
        for category in categories:
            self.category_combo.addItem(category.name, userData=category.id)
        self.layout.addWidget(QLabel("Category:"))
        self.layout.addWidget(self.category_combo)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        self.layout.addWidget(self.notes_input)

        # Dialog buttons (Save/Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def open_password_generator(self):
        """Opens the password generator dialog and populates the password field."""
        dialog = PasswordGeneratorScreen(self)
        if dialog.exec():
            password = dialog.get_password()
            if "Click 'Generate'" not in password: # Avoid setting placeholder text
                self.password_input.setText(password)

    def get_entry_data(self):
        """Returns the data entered by the user."""
        return {
            "title": self.title_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "url": self.url_input.text(),
            "category": self.category_combo.currentData(),
            "notes": self.notes_input.toPlainText()
        }
