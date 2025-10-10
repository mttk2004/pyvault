from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Signal

class LoginScreen(QWidget):
    # This signal now only carries the password. The controller knows the context.
    login_attempted = Signal(str)

    def __init__(self):
        super().__init__()
        self.mode = 'unlock'  # Default mode
        self.layout = QVBoxLayout(self)

        # Title
        self.title = QLabel("Unlock Vault")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title)

        # Master Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Master Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        # Confirm Master Password Input (hidden by default)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Master Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.hide()
        self.layout.addWidget(self.confirm_password_input)

        # Action Button (for Unlock or Create)
        self.action_button = QPushButton("Unlock")
        self.action_button.clicked.connect(self.on_action_button_clicked)
        self.layout.addWidget(self.action_button)

    def set_mode(self, mode):
        """
        Switches the UI between 'create' and 'unlock' modes.
        """
        self.mode = mode
        if mode == 'create':
            self.title.setText("Create New Vault")
            self.confirm_password_input.show()
            self.action_button.setText("Create Vault")
        else: # 'unlock'
            self.title.setText("Unlock Vault")
            self.confirm_password_input.hide()
            self.action_button.setText("Unlock")
        self.clear_fields()

    def on_action_button_clicked(self):
        """
        Handles the click of the main action button, validating input
        based on the current mode.
        """
        password = self.password_input.text()

        if not password:
            QMessageBox.warning(self, "Input Error", "Password cannot be empty.")
            return

        if self.mode == 'create':
            confirm_password = self.confirm_password_input.text()
            if password != confirm_password:
                QMessageBox.warning(self, "Input Error", "Passwords do not match.")
                return

        self.login_attempted.emit(password)

    def clear_fields(self):
        """Clears all password input fields."""
        self.password_input.clear()
        self.confirm_password_input.clear()
