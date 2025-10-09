"""
Custom Qt Table Model for PyVault entries.
"""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor, QBrush

from ..category_manager import CategoryManager

class EntryTableModel(QAbstractTableModel):
    """A custom table model for displaying vault entries."""

    def __init__(self, data=None, headers=None, category_manager=None, parent=None):
        super().__init__(parent)
        self.table_data = data or []
        self.headers = headers or []
        self.category_manager = category_manager

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows."""
        return len(self.table_data)

    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns."""
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Return data for a given index and role."""
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        entry = self.table_data[row]

        if role == Qt.ItemDataRole.DisplayRole:
            header_key = self.headers[col].lower().replace(" ", "_")
            if header_key == "category":
                category_id = entry.get("category", CategoryManager.UNCATEGORIZED_ID)
                category = self.category_manager.get_category(category_id)
                return category.name if category else "Uncategorized"
            elif header_key == "password":
                return "••••••••"
            else:
                return entry.get(header_key, "")
        elif role == Qt.ItemDataRole.UserRole:
            # Store the original index of the entry
            return row
        elif role == Qt.ItemDataRole.BackgroundRole and self.headers[col] == "Category":
            category_id = entry.get("category", CategoryManager.UNCATEGORIZED_ID)
            category = self.category_manager.get_category(category_id)
            if category:
                return QBrush(QColor(category.color))
        elif role == Qt.ItemDataRole.ForegroundRole and self.headers[col] == "Category":
            category_id = entry.get("category", CategoryManager.UNCATEGORIZED_ID)
            category = self.category_manager.get_category(category_id)
            if category:
                contrast_color = self.category_manager.get_contrast_color(category.color)
                return QBrush(QColor(contrast_color))

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Return header data."""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def set_data(self, data):
        """Set new data for the model."""
        self.beginResetModel()
        self.table_data = data
        self.endResetModel()

    def get_entry(self, row):
        """Get the entry data for a specific row."""
        if 0 <= row < len(self.table_data):
            return self.table_data[row]
        return None
