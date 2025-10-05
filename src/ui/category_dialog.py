"""
Category Management Dialog for PyVault
Provides UI for creating, editing, and deleting categories with color selection.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QColorDialog, QMessageBox, QWidget, QFrame, QGroupBox,
    QSizePolicy, QSpacerItem, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QPixmap, QPainter, QFont, QIcon

from ..category_manager import CategoryManager, Category

class ColorButton(QPushButton):
    """Custom button that displays and allows selection of colors."""
    
    color_changed = Signal(str)
    
    def __init__(self, color: str = "#6c757d", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(40, 40)
        self.clicked.connect(self._choose_color)
        self._update_appearance()
    
    def set_color(self, color: str):
        """Set the button color."""
        self._color = color
        self._update_appearance()
    
    def get_color(self) -> str:
        """Get the current color."""
        return self._color
    
    def _update_appearance(self):
        """Update button appearance to show the color."""
        # Create a pixmap with the color
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(self._color))
        
        # Draw border
        painter = QPainter(pixmap)
        painter.setPen(QColor("#dee2e6"))
        painter.drawRect(0, 0, 31, 31)
        painter.end()
        
        self.setIcon(QIcon(pixmap))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid #dee2e6;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                border-color: #adb5bd;
            }}
            QPushButton:pressed {{
                background-color: {self._lighten_color(self._color)};
            }}
        """)
    
    def _lighten_color(self, color: str) -> str:
        """Lighten a color by 10%."""
        qcolor = QColor(color)
        h, s, l, a = qcolor.getHsl()
        qcolor.setHsl(h, s, min(255, int(l * 1.1)), a)
        return qcolor.name()
    
    def _choose_color(self):
        """Open color picker dialog."""
        initial_color = QColor(self._color)
        color = QColorDialog.getColor(initial_color, self, "Choose Category Color")
        
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
        """Setup the item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Category color indicator
        color_frame = QFrame()
        color_frame.setFixedSize(20, 20)
        color_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.category.color};
                border: 1px solid #dee2e6;
                border-radius: 10px;
            }}
        """)
        layout.addWidget(color_frame)
        
        # Category info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Name and icon
        name_label = QLabel(f"{self.category.icon} {self.category.name}")
        name_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #1d1d1f;
        """)
        info_layout.addWidget(name_label)
        
        # Entry count
        count_label = QLabel(f"{self.entry_count} entries")
        count_label.setStyleSheet("""
            font-size: 12px;
            color: #86868b;
        """)
        info_layout.addWidget(count_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()

class CategoryDialog(QDialog):
    """Dialog for managing password entry categories."""
    
    categories_changed = Signal()
    
    def __init__(self, category_manager: CategoryManager, entries: list, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.entries = entries
        self.current_category = None
        
        self.setWindowTitle("Manage Categories")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        self._setup_ui()
        self._refresh_category_list()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left side - Category list
        left_panel = self._create_category_list_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right side - Category editor
        right_panel = self._create_category_editor_panel()
        main_layout.addWidget(right_panel, 1)
    
    def _create_category_list_panel(self) -> QWidget:
        """Create the category list panel."""
        panel = QGroupBox("Categories")
        panel.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #1d1d1f;
                border: 2px solid #e5e5e5;
                border-radius: 10px;
                padding-top: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Category list
        self.category_list = QListWidget()
        self.category_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.category_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #f1f3f5;
                padding: 0px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 3px solid #2196f3;
            }
            QListWidget::item:hover {
                background-color: #f5f5f7;
            }
        """)
        self.category_list.itemClicked.connect(self._on_category_selected)
        layout.addWidget(self.category_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_category_btn = QPushButton("+ Add Category")
        self.add_category_btn.clicked.connect(self._add_new_category)
        self.add_category_btn.setStyleSheet(self._get_primary_button_style())
        
        self.delete_category_btn = QPushButton("Delete")
        self.delete_category_btn.clicked.connect(self._delete_category)
        self.delete_category_btn.setEnabled(False)
        self.delete_category_btn.setStyleSheet(self._get_danger_button_style())
        
        button_layout.addWidget(self.add_category_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.delete_category_btn)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def _create_category_editor_panel(self) -> QWidget:
        """Create the category editor panel."""
        panel = QGroupBox("Category Editor")
        panel.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #1d1d1f;
                border: 2px solid #e5e5e5;
                border-radius: 10px;
                padding-top: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        
        # Form for editing
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        
        # Name field
        name_label = QLabel("Name:")
        name_label.setStyleSheet("font-weight: 500; color: #1d1d1f;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Category name")
        self.name_input.setStyleSheet(self._get_input_style())
        self.name_input.textChanged.connect(self._on_form_changed)
        form_layout.addRow(name_label, self.name_input)
        
        # Color field
        color_label = QLabel("Color:")
        color_label.setStyleSheet("font-weight: 500; color: #1d1d1f;")
        self.color_button = ColorButton()
        self.color_button.color_changed.connect(self._on_color_changed)
        form_layout.addRow(color_label, self.color_button)
        
        # Icon field
        icon_label = QLabel("Icon:")
        icon_label.setStyleSheet("font-weight: 500; color: #1d1d1f;")
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("📁")
        self.icon_input.setMaxLength(2)  # Emoji are typically 1-2 characters
        self.icon_input.setStyleSheet(self._get_input_style())
        self.icon_input.textChanged.connect(self._on_form_changed)
        form_layout.addRow(icon_label, self.icon_input)
        
        layout.addLayout(form_layout)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("Select a category to edit")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 20px;
                color: #86868b;
                font-size: 14px;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        layout.addStretch()
        
        # Save/Cancel buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_edit)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet(self._get_secondary_button_style())
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self._save_category)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet(self._get_primary_button_style())
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # Close button at bottom
        close_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(self._get_secondary_button_style())
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        close_layout.addStretch()
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(panel)
        main_layout.addLayout(close_layout)
        
        container = QWidget()
        container.setLayout(main_layout)
        return container
    
    def _refresh_category_list(self):
        """Refresh the category list."""
        self.category_list.clear()
        
        # Get entry counts
        entry_counts = self.category_manager.count_entries_by_category(self.entries)
        
        categories = self.category_manager.get_all_categories()
        for category in categories:
            count = entry_counts.get(category.id, 0)
            
            # Create custom widget
            item_widget = CategoryListItem(category, count)
            
            # Create list item
            list_item = QListWidgetItem()
            list_item.setData(Qt.ItemDataRole.UserRole, category.id)
            list_item.setSizeHint(item_widget.sizeHint())
            
            self.category_list.addItem(list_item)
            self.category_list.setItemWidget(list_item, item_widget)
    
    def _on_category_selected(self, item: QListWidgetItem):
        """Handle category selection."""
        category_id = item.data(Qt.ItemDataRole.UserRole)
        category = self.category_manager.get_category(category_id)
        
        if category:
            self.current_category = category
            self._load_category_to_form(category)
            
            # Enable/disable delete button
            can_delete = category_id != CategoryManager.UNCATEGORIZED_ID
            self.delete_category_btn.setEnabled(can_delete)
    
    def _load_category_to_form(self, category: Category):
        """Load category data into the form."""
        self.name_input.setText(category.name)
        self.color_button.set_color(category.color)
        self.icon_input.setText(category.icon)
        
        self._update_preview()
        self._enable_editing(True)
    
    def _update_preview(self):
        """Update the preview display."""
        if not self.current_category:
            return
        
        name = self.name_input.text() or self.current_category.name
        color = self.color_button.get_color()
        icon = self.icon_input.text() or self.current_category.icon
        
        contrast_color = CategoryManager.get_contrast_color(color)
        
        self.preview_label.setText(f"{icon} {name}")
        self.preview_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: {contrast_color};
                border: 2px solid {color};
                border-radius: 8px;
                padding: 20px;
                font-size: 16px;
                font-weight: 500;
            }}
        """)
    
    def _enable_editing(self, enabled: bool):
        """Enable/disable editing controls."""
        self.name_input.setEnabled(enabled)
        self.color_button.setEnabled(enabled)
        self.icon_input.setEnabled(enabled)
        self.save_btn.setEnabled(False)  # Will be enabled when form changes
        self.cancel_btn.setEnabled(enabled)
        
        # Disable name editing for uncategorized
        if enabled and self.current_category and self.current_category.id == CategoryManager.UNCATEGORIZED_ID:
            self.name_input.setEnabled(False)
    
    def _on_form_changed(self):
        """Handle form changes."""
        if self.current_category:
            self.save_btn.setEnabled(True)
            self._update_preview()
    
    def _on_color_changed(self, color: str):
        """Handle color changes."""
        self._on_form_changed()
    
    def _add_new_category(self):
        """Add a new category."""
        try:
            category = self.category_manager.create_category("New Category")
            self._refresh_category_list()
            
            # Select the new category
            for i in range(self.category_list.count()):
                item = self.category_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == category.id:
                    self.category_list.setCurrentItem(item)
                    self._on_category_selected(item)
                    self.name_input.selectAll()
                    self.name_input.setFocus()
                    break
            
            self.categories_changed.emit()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def _delete_category(self):
        """Delete the selected category."""
        if not self.current_category or self.current_category.id == CategoryManager.UNCATEGORIZED_ID:
            return
        
        # Count entries in this category
        entry_counts = self.category_manager.count_entries_by_category(self.entries)
        entry_count = entry_counts.get(self.current_category.id, 0)
        
        # Confirm deletion
        if entry_count > 0:
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"The category '{self.current_category.name}' contains {entry_count} entries. "
                "These entries will be moved to 'Uncategorized'. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        else:
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the category '{self.current_category.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Move entries to uncategorized
                for entry in self.entries:
                    if entry.get("category") == self.current_category.id:
                        entry["category"] = CategoryManager.UNCATEGORIZED_ID
                
                # Delete the category
                self.category_manager.delete_category(self.current_category.id)
                
                # Refresh UI
                self.current_category = None
                self._refresh_category_list()
                self._clear_form()
                
                self.categories_changed.emit()
                
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
    
    def _save_category(self):
        """Save category changes."""
        if not self.current_category:
            return
        
        name = self.name_input.text().strip()
        color = self.color_button.get_color()
        icon = self.icon_input.text().strip() or "📁"
        
        if not name:
            QMessageBox.warning(self, "Error", "Category name cannot be empty.")
            self.name_input.setFocus()
            return
        
        try:
            self.category_manager.update_category(
                self.current_category.id,
                name=name,
                color=color,
                icon=icon
            )
            
            self._refresh_category_list()
            self.save_btn.setEnabled(False)
            self.categories_changed.emit()
            
            QMessageBox.information(self, "Success", "Category updated successfully!")
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def _cancel_edit(self):
        """Cancel editing."""
        if self.current_category:
            self._load_category_to_form(self.current_category)
        self.save_btn.setEnabled(False)
    
    def _clear_form(self):
        """Clear the form."""
        self.name_input.clear()
        self.color_button.set_color("#6c757d")
        self.icon_input.clear()
        self.preview_label.setText("Select a category to edit")
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 20px;
                color: #86868b;
                font-size: 14px;
            }
        """)
        self._enable_editing(False)
    
    def _get_primary_button_style(self) -> str:
        """Get primary button style."""
        return """
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """
    
    def _get_secondary_button_style(self) -> str:
        """Get secondary button style."""
        return """
            QPushButton {
                background-color: transparent;
                color: #1d1d1f;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f5f5f7;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
            }
            QPushButton:disabled {
                color: #9e9e9e;
                border-color: #e0e0e0;
            }
        """
    
    def _get_danger_button_style(self) -> str:
        """Get danger button style."""
        return """
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #9e9e9e;
            }
        """
    
    def _get_input_style(self) -> str:
        """Get input field style."""
        return """
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                color: #495057;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                outline: none;
            }
            QLineEdit:disabled {
                background-color: #f8f9fa;
                color: #86868b;
            }
        """
