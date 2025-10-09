"""
PyVault Category Dialog - V2 (Bitwarden Inspired)
A redesigned modal for managing categories.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QColorDialog, QMessageBox, QWidget, QFrame, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QSize, Slot
from PySide6.QtGui import QColor, QPixmap, QPainter, QIcon

from .design_system import tokens, get_global_stylesheet
from ..category_manager import CategoryManager, Category
from .design_system import tokens

class ColorButton(QPushButton):
    """Custom button that displays and allows selection of colors."""

    color_changed = Signal(str)

    def __init__(self, color: str = "#6c757d", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(36, 36)
        self.clicked.connect(self._choose_color)
        self._update_appearance()

    def set_color(self, color: str):
        self._color = color
        self._update_appearance()

    def get_color(self) -> str:
        return self._color

    def _update_appearance(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 1px solid {tokens.colors.border};
                border-radius: {tokens.border_radius.md}px;
            }}
            QPushButton:hover {{
                border-color: {tokens.colors.border_hover};
            }}
        """)

    def _choose_color(self):
        color = QColorDialog.getColor(QColor(self._color), self, "Choose Category Color")
        if color.isValid():
            self._color = color.name()
            self._update_appearance()
            self.color_changed.emit(self._color)

class CategoryListItem(QWidget):
    """Custom widget for displaying category in the list."""

    def __init__(self, category: Category, entry_count: int = 0, parent=None):
        super().__init__(parent)
        self.category = category
        self.entry_count = entry_count
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        color_frame = QFrame()
        color_frame.setFixedSize(16, 16)
        color_frame.setStyleSheet(f"background-color: {self.category.color}; border-radius: 8px;")
        layout.addWidget(color_frame)

        name_label = QLabel(f"{self.category.icon} {self.category.name}")
        name_label.setStyleSheet(f"font-size: {tokens.typography.text_sm}px; font-weight: {tokens.typography.font_medium};")

        count_label = QLabel(f"{self.entry_count} entries")
        count_label.setStyleSheet(f"font-size: {tokens.typography.text_xs}px; color: {tokens.colors.text_tertiary};")

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.addWidget(name_label)
        info_layout.addWidget(count_label)

        layout.addLayout(info_layout)
        layout.addStretch()

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
        self.setMinimumSize(700, 500)

        self._setup_ui()
        self.setStyleSheet(get_global_stylesheet())
        self._refresh_category_list()
        self._apply_styles()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(tokens.spacing.lg)
        main_layout.setContentsMargins(tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg, tokens.spacing.lg)

        left_panel = self._create_category_list_panel()
        main_layout.addWidget(left_panel, 1)

        right_panel = self._create_category_editor_panel()
        main_layout.addWidget(right_panel, 2)

    def _create_category_list_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(tokens.spacing.md)

        title = QLabel("Categories")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        self.category_list = QListWidget()
        self.category_list.itemClicked.connect(self._on_category_selected)
        layout.addWidget(self.category_list)

        self.add_category_btn = QPushButton("New Category")
        self.add_category_btn.clicked.connect(self._add_new_category)
        self.add_category_btn.setObjectName("primaryButton")
        layout.addWidget(self.add_category_btn)

        return panel

    def _create_category_editor_panel(self) -> QWidget:
        panel = QWidget()
        self.editor_layout = QVBoxLayout(panel)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(tokens.spacing.md)

        self.editor_label = QLabel("Select a category to edit or create a new one.")
        self.editor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.editor_layout.addWidget(self.editor_label)

        self.editor_form = QWidget()
        self.editor_form.hide()
        form_layout = QFormLayout(self.editor_form)
        form_layout.setSpacing(tokens.spacing.md)

        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(self._on_form_changed)
        form_layout.addRow(QLabel("Name"), self.name_input)

        self.icon_input = QLineEdit()
        self.icon_input.setMaxLength(2)
        self.icon_input.textChanged.connect(self._on_form_changed)
        form_layout.addRow(QLabel("Icon"), self.icon_input)

        self.color_button = ColorButton()
        self.color_button.color_changed.connect(self._on_color_changed)
        form_layout.addRow(QLabel("Color"), self.color_button)

        self.editor_layout.addWidget(self.editor_form)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.delete_category_btn = QPushButton("Delete")
        self.delete_category_btn.clicked.connect(self._delete_category)
        self.delete_category_btn.setObjectName("dangerButton")
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self._save_category)
        self.save_btn.setObjectName("primaryButton")
        button_layout.addWidget(self.delete_category_btn)
        button_layout.addWidget(self.save_btn)

        self.editor_layout.addStretch()
        self.editor_layout.addLayout(button_layout)

        return panel

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QDialog {{ background-color: {tokens.colors.surface}; }}
            QLabel#dialogTitle {{
                font-size: {tokens.typography.text_xl}px;
                font-weight: {tokens.typography.font_semibold};
                color: {tokens.colors.text_primary};
            }}
            QListWidget {{
                border: 1px solid {tokens.colors.border};
                border-radius: {tokens.border_radius.md}px;
            }}
            QListWidget::item:selected {{
                background-color: {tokens.colors.primary_light};
            }}
            QLineEdit {{
                padding: {tokens.spacing.sm}px;
                border: 1px solid {tokens.colors.border};
                border-radius: {tokens.border_radius.md}px;
            }}
            QPushButton#primaryButton {{
                background-color: {tokens.colors.primary};
                color: white;
                border: none;
                padding: {tokens.spacing.sm}px {tokens.spacing.lg}px;
                border-radius: {tokens.border_radius.md}px;
            }}
            QPushButton#dangerButton {{
                background-color: {tokens.colors.error};
                color: white;
                border: none;
                padding: {tokens.spacing.sm}px {tokens.spacing.lg}px;
                border-radius: {tokens.border_radius.md}px;
            }}
        """)
        self.editor_label.setStyleSheet(f"color: {tokens.colors.text_tertiary};")

    def _refresh_category_list(self):
        self.category_list.clear()
        entry_counts = self.category_manager.count_entries_by_category(self.entries)

        for category in self.category_manager.get_all_categories():
            count = entry_counts.get(category.id, 0)
            item_widget = CategoryListItem(category, count)
            list_item = QListWidgetItem()
            list_item.setData(Qt.ItemDataRole.UserRole, category.id)
            list_item.setSizeHint(item_widget.sizeHint())
            self.category_list.addItem(list_item)
            self.category_list.setItemWidget(list_item, item_widget)

    def _on_category_selected(self, item: QListWidgetItem):
        category_id = item.data(Qt.ItemDataRole.UserRole)
        category = self.category_manager.get_category(category_id)
        if category:
            self.current_category = category
            self._load_category_to_form(category)
            self.editor_label.hide()
            self.editor_form.show()

    def _load_category_to_form(self, category: Category):
        self.name_input.setText(category.name)
        self.color_button.set_color(category.color)
        self.icon_input.setText(category.icon)
        self.save_btn.setEnabled(False)
        self.delete_category_btn.setEnabled(category.id != CategoryManager.UNCATEGORIZED_ID)

    def _on_form_changed(self):
        if self.current_category:
            self.save_btn.setEnabled(True)

    def _on_color_changed(self, color: str):
        self._on_form_changed()

    @Slot()
    def _add_new_category(self):
        try:
            new_cat = self.category_manager.create_category("New Category")
            self.categories_changed.emit()
            self._refresh_category_list()
            self.categories_changed.emit()
            # Select the new category for immediate editing
            for i in range(self.category_list.count()):
                item = self.category_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == category.id:
                    self.category_list.setCurrentRow(i)
                    self._on_category_selected(item)
                    break
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _delete_category(self):
        if not self.current_category or self.current_category.id == CategoryManager.UNCATEGORIZED_ID:
            return

        reply = QMessageBox.question(self, "Confirm Delete",
            f"Delete '{self.current_category.name}'? Entries will be moved to Uncategorized.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            for entry in self.entries:
                if entry.get("category") == self.current_category.id:
                    entry["category"] = CategoryManager.UNCATEGORIZED_ID
            self.category_manager.delete_category(self.current_category.id)
            self.categories_changed.emit()
            self._refresh_category_list()
            self.editor_form.hide()
            self.editor_label.show()

    def _save_category(self):
        if not self.current_category: return

        try:
            self.category_manager.update_category(
                self.current_category.id,
                name=self.name_input.text().strip(),
                color=self.color_button.get_color(),
                icon=self.icon_input.text().strip() or "📁"
            )
            self.categories_changed.emit()
            self._refresh_category_list()
            self.save_btn.setEnabled(False)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
