import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVault - Your Personal Vault")
        self.setMinimumSize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self._setup_ui()

    def _setup_ui(self):
        """Sets up the main UI components."""
        # Button layout
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New")
        self.edit_button = QPushButton("Edit Selected")
        self.delete_button = QPushButton("Delete Selected")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch() # Pushes buttons to the left

        self.layout.addLayout(button_layout)

        # Table for credentials
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Service", "Username", "Password", "URL"])

        # Style the table
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Read-only
        self.table_widget.verticalHeader().setVisible(False)

        self.layout.addWidget(self.table_widget)

    def populate_table(self, data: list[dict]):
        """
        Populates the table with decrypted vault data.
        Each item in the list is a dictionary with 'service', 'username', 'password', 'url'.
        """
        self.table_widget.setRowCount(len(data))
        for row, item in enumerate(data):
            self.table_widget.setItem(row, 0, QTableWidgetItem(item.get("service", "")))
            self.table_widget.setItem(row, 1, QTableWidgetItem(item.get("username", "")))
            # For security, we might just show '********' for the password
            self.table_widget.setItem(row, 2, QTableWidgetItem("********"))
            self.table_widget.setItem(row, 3, QTableWidgetItem(item.get("url", "")))

# Example usage for testing the UI component directly
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Example data
    test_data = [
        {"service": "Google", "username": "test@gmail.com", "password": "123", "url": "google.com"},
        {"service": "GitHub", "username": "test-user", "password": "456", "url": "github.com"},
    ]

    main_win = MainWindow()
    main_win.populate_table(test_data)
    main_win.show()

    sys.exit(app.exec())
