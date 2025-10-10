from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QListWidgetItem,
    QColorDialog
)
from src.category_manager import CategoryManager, Category

class CategoryScreen(QDialog):
    def __init__(self, category_manager: CategoryManager, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager

        self.setWindowTitle("Manage Categories")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        # List to display categories
        self.category_list = QListWidget()
        self.populate_categories()
        self.layout.addWidget(self.category_list)

        # Buttons for actions
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.close_button = QPushButton("Close")

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.close_button)

        self.layout.addLayout(self.button_layout)

        # Connect signals
        self.add_button.clicked.connect(self.add_category)
        self.edit_button.clicked.connect(self.edit_category)
        self.delete_button.clicked.connect(self.delete_category)
        self.close_button.clicked.connect(self.accept)

    def populate_categories(self):
        """Clears and refills the list of categories from the manager."""
        self.category_list.clear()
        for category in self.category_manager.get_all_categories():
            item = QListWidgetItem(category.name)
            item.setData(1, category.id)  # Use a role to store the ID
            self.category_list.addItem(item)

    def add_category(self):
        """Opens a dialog to add a new category."""
        name, ok = QInputDialog.getText(self, "Add Category", "Enter category name:")
        if ok and name:
            try:
                color = QColorDialog.getColor()
                if color.isValid():
                    self.category_manager.create_category(name, color.name())
                    self.populate_categories()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def edit_category(self):
        """Opens a dialog to edit the selected category."""
        selected_item = self.category_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Please select a category to edit.")
            return

        category_id = selected_item.data(1)
        category = self.category_manager.get_category(category_id)

        if category_id == self.category_manager.UNCATEGORIZED_ID:
            QMessageBox.information(self, "Information", "The 'Uncategorized' category cannot be edited.")
            return

        new_name, ok = QInputDialog.getText(self, "Edit Category", "Enter new name:", text=category.name)
        if ok and new_name:
            try:
                self.category_manager.update_category(category_id, name=new_name)
                self.populate_categories()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def delete_category(self):
        """Deletes the selected category after confirmation."""
        selected_item = self.category_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Please select a category to delete.")
            return

        category_id = selected_item.data(1)
        if category_id == self.category_manager.UNCATEGORIZED_ID:
            QMessageBox.warning(self, "Error", "Cannot delete the 'Uncategorized' category.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the category '{selected_item.text()}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.category_manager.delete_category(category_id)
            self.populate_categories()
