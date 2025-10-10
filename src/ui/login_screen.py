from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog
from PySide6.QtCore import Signal

class LoginScreen(QWidget):
    login_successful = Signal(str, str) # vault_path, password

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Title
        self.title = QLabel("PyVault")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title)

        # Vault Path Input
        self.path_layout = QHBoxLayout()
        self.vault_path = QLineEdit()
        self.vault_path.setPlaceholderText("Path to your vault file")
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_for_vault)
        self.path_layout.addWidget(self.vault_path)
        self.path_layout.addWidget(self.browse_button)
        self.layout.addLayout(self.path_layout)

        # Master Password Input
        self.password = QLineEdit()
        self.password.setPlaceholderText("Master Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.unlock_button = QPushButton("Unlock")
        self.create_button = QPushButton("Create New Vault")
        self.unlock_button.clicked.connect(self.unlock_vault)
        self.create_button.clicked.connect(self.create_vault)
        self.button_layout.addWidget(self.unlock_button)
        self.button_layout.addWidget(self.create_button)
        self.layout.addLayout(self.button_layout)

    def browse_for_vault(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Vault File", "", "PyVault Files (*.json)")
        if file_path:
            self.vault_path.setText(file_path)

    def unlock_vault(self):
        vault_path = self.vault_path.text()
        password = self.password.text()
        if vault_path and password:
            self.login_successful.emit(vault_path, password)

    def create_vault(self):
        # This will be handled in the main application logic
        # For now, we can just signal that the user wants to create a vault
        # Or we can handle the file dialog here. Let's do that.
        file_path, _ = QFileDialog.getSaveFileName(self, "Create New Vault", "", "PyVault Files (*.json)")
        if file_path:
            self.vault_path.setText(file_path)
            # A new vault still requires a password to be set by the user
            # We can reuse the login_successful signal, and the main logic will check if the file exists
            password = self.password.text()
            if password:
                self.login_successful.emit(file_path, password)
