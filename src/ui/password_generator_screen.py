import random
import string
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QCheckBox,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard

class PasswordGeneratorScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Generator")
        self.setMinimumWidth(350)

        self.layout = QVBoxLayout(self)

        # Generated Password Display
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setText("Click 'Generate' to create a password.")
        self.layout.addWidget(self.password_display)

        # Length Slider
        self.length_layout = QHBoxLayout()
        self.length_label = QLabel("Length: 16")
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(64)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.update_length_label)
        self.length_layout.addWidget(self.length_label)
        self.length_layout.addWidget(self.length_slider)
        self.layout.addLayout(self.length_layout)

        # Options
        self.uppercase_check = QCheckBox("Include Uppercase (A-Z)")
        self.uppercase_check.setChecked(True)
        self.numbers_check = QCheckBox("Include Numbers (0-9)")
        self.numbers_check.setChecked(True)
        self.symbols_check = QCheckBox("Include Symbols (!@#$%)")
        self.symbols_check.setChecked(True)

        self.layout.addWidget(self.uppercase_check)
        self.layout.addWidget(self.numbers_check)
        self.layout.addWidget(self.symbols_check)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate")
        self.copy_button = QPushButton("Copy")
        self.close_button = QPushButton("Close")

        self.button_layout.addWidget(self.generate_button)
        self.button_layout.addWidget(self.copy_button)
        self.button_layout.addWidget(self.close_button)

        self.layout.addLayout(self.button_layout)

        # Connect signals
        self.generate_button.clicked.connect(self.generate_password)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.close_button.clicked.connect(self.accept)

    def update_length_label(self, value):
        self.length_label.setText(f"Length: {value}")

    def generate_password(self):
        length = self.length_slider.value()
        use_uppercase = self.uppercase_check.isChecked()
        use_numbers = self.numbers_check.isChecked()
        use_symbols = self.symbols_check.isChecked()

        char_set = string.ascii_lowercase
        if use_uppercase:
            char_set += string.ascii_uppercase
        if use_numbers:
            char_set += string.digits
        if use_symbols:
            char_set += string.punctuation

        if not char_set:
            self.password_display.setText("Select at least one character type.")
            return

        password = ''.join(random.choice(char_set) for _ in range(length))
        self.password_display.setText(password)

    def copy_to_clipboard(self):
        clipboard = QClipboard()
        clipboard.setText(self.password_display.text())
        QMessageBox.information(self, "Copied", "Password copied to clipboard!")

    def get_password(self):
        """Returns the generated password."""
        return self.password_display.text()
