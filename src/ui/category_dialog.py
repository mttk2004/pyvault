"""
PyVault Category Dialog - V2 (Bitwarden Inspired)
A redesigned modal for managing categories.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QColorDialog, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from .design_system import tokens, get_global_stylesheet
from ..category_manager import CategoryManager, Category

class CategoryDialog(QDialog):
    """A clean, dark-themed dialog for managing categories."""
    
    categories_changed = Signal()
    
    def __init__(self, category_manager: CategoryManager, entries: list, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.entries = entries
        self.current_category_id = None
        
        self.setWindowTitle("Manage Categories")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        
        self._setup_ui()
        self.setStyleSheet(get_global_stylesheet())
        self._refresh_category_list()
        self._show_editor_for_category(None) # Start with editor hidden

    def _setup_ui(self):
        """Setup the two-panel UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(tokens.spacing.lg)
        main_layout.setContentsMargins(tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg)

        # --- Left Panel (List) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(tokens.spacing.md)

        list_title = QLabel("Categories")
        list_title.setStyleSheet(f"font-size: {tokens.typography.text_lg}pt; font-weight: {tokens.typography.font_semibold};")
        
        self.category_list = QListWidget()
        self.category_list.currentItemChanged.connect(self._on_category_selected)
        
        add_button = QPushButton("Add Category")
        add_button.setObjectName("PrimaryButton")
        add_button.clicked.connect(self._add_new_category)
        
        left_layout.addWidget(list_title)
        left_layout.addWidget(self.category_list)
        left_layout.addWidget(add_button)

        # --- Right Panel (Editor) ---
        right_panel = QWidget()
        self.editor_layout = QVBoxLayout(right_panel)
        self.editor_layout.setSpacing(tokens.spacing.md)
        
        self.editor_title = QLabel("Select a Category")
        self.editor_title.setStyleSheet(f"font-size: {tokens.typography.text_lg}pt; font-weight: {tokens.typography.font_semibold};")
        
        self.editor_form = QWidget()
        form_layout = QFormLayout(self.editor_form)
        form_layout.setSpacing(tokens.spacing.md)
        
        self.name_input = QLineEdit()
        self.icon_input = QLineEdit()
        self.icon_input.setMaxLength(2)
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self._choose_color)
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Icon:", self.icon_input)
        form_layout.addRow("Color:", self.color_button)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("dangerButton") # Style this in stylesheet
        self.delete_button.clicked.connect(self._delete_category)
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("PrimaryButton")
        self.save_button.clicked.connect(self._save_category)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.save_button)

        self.editor_layout.addWidget(self.editor_title)
        self.editor_layout.addWidget(self.editor_form)
        self.editor_layout.addStretch()
        self.editor_layout.addLayout(button_layout)
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def _refresh_category_list(self):
        """Repopulate the category list."""
        self.category_list.clear()
        counts = self.category_manager.count_entries_by_category(self.entries)
        for cat in self.category_manager.get_all_categories():
            item = QListWidgetItem(f"{cat.icon} {cat.name} ({counts.get(cat.id, 0)})")
            item.setData(Qt.ItemDataRole.UserRole, cat.id)
            self.category_list.addItem(item)

    @Slot()
    def _on_category_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle list selection changes."""
        if current:
            category_id = current.data(Qt.ItemDataRole.UserRole)
            category = self.category_manager.get_category(category_id)
            self._show_editor_for_category(category)
        else:
            self._show_editor_for_category(None)

    def _show_editor_for_category(self, category: Category | None):
        """Update the editor panel for the selected category."""
        if category:
            self.current_category_id = category.id
            self.editor_title.setText(f"Edit '{category.name}'")
            self.name_input.setText(category.name)
            self.icon_input.setText(category.icon)
            self._set_color(category.color)

            is_uncategorized = category.id == CategoryManager.UNCATEGORIZED_ID
            self.name_input.setReadOnly(is_uncategorized)
            self.delete_button.setEnabled(not is_uncategorized)

            self.editor_form.show()
            self.save_button.show()
            self.delete_button.show()
        else:
            self.current_category_id = None
            self.editor_title.setText("Select a category")
            self.editor_form.hide()
            self.save_button.hide()
            self.delete_button.hide()
    
    @Slot()
    def _choose_color(self):
        """Open a color picker dialog."""
        current_color = self.color_button.property("color")
        color = QColorDialog.getColor(QColor(current_color), self)
        if color.isValid():
            self._set_color(color.name())

    def _set_color(self, color_hex: str):
        """Set the color of the color button."""
        self.color_button.setProperty("color", color_hex)
        self.color_button.setStyleSheet(f"background-color: {color_hex}; border: 1px solid {tokens.colors.border_primary};")
    
    @Slot()
    def _add_new_category(self):
        try:
            new_cat = self.category_manager.create_category("New Category")
            self.categories_changed.emit()
            self._refresh_category_list()
            # Find and select the new category
            for i in range(self.category_list.count()):
                if self.category_list.item(i).data(Qt.ItemDataRole.UserRole) == new_cat.id:
                    self.category_list.setCurrentRow(i)
                    break
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    @Slot()
    def _save_category(self):
        if not self.current_category_id: return
        
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Category name cannot be empty.")
            return

        try:
            self.category_manager.update_category(
                self.current_category_id,
                name=name,
                icon=self.icon_input.text().strip(),
                color=self.color_button.property("color")
            )
            self.categories_changed.emit()
            self._refresh_category_list()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    @Slot()
    def _delete_category(self):
        if not self.current_category_id or self.current_category_id == CategoryManager.UNCATEGORIZED_ID:
            return

        cat = self.category_manager.get_category(self.current_category_id)
        reply = QMessageBox.question(self, "Confirm Delete",
            f"Are you sure you want to delete '{cat.name}'? Entries will be moved to 'Uncategorized'.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Reassign entries before deleting
            for entry in self.entries:
                if entry.get("category") == self.current_category_id:
                    entry["category"] = CategoryManager.UNCATEGORIZED_ID

            self.category_manager.delete_category(self.current_category_id)
            self.categories_changed.emit()
            self._refresh_category_list()
            self._show_editor_for_category(None)
