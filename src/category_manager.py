"""
Category Management System for PyVault
Provides CRUD operations for password entry categories with color coding.
"""

import uuid
from typing import Dict, List, Optional, Tuple
from PySide6.QtGui import QColor

class Category:
    """Represents a password entry category with metadata."""
    
    def __init__(self, id: str = None, name: str = "", color: str = "#6c757d", icon: str = "📁"):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.color = color  # Hex color string
        self.icon = icon
        self.created_at = None  # Could add timestamp if needed
        
    def to_dict(self) -> Dict:
        """Convert category to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "icon": self.icon
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Category':
        """Create category from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            color=data.get("color", "#6c757d"),
            icon=data.get("icon", "📁")
        )
    
    def __str__(self):
        return f"{self.icon} {self.name}"
    
    def __eq__(self, other):
        if isinstance(other, Category):
            return self.id == other.id
        return False

class CategoryManager:
    """Manages categories for password entries."""
    
    # Default category that cannot be deleted
    UNCATEGORIZED_ID = "uncategorized"
    
    def __init__(self):
        self.categories: Dict[str, Category] = {}
        self._create_default_categories()
        
    def _create_default_categories(self):
        """Create default categories."""
        # Uncategorized category (always present)
        uncategorized = Category(
            id=self.UNCATEGORIZED_ID,
            name="Uncategorized",
            color="#6c757d",
            icon="📂"
        )
        self.categories[self.UNCATEGORIZED_ID] = uncategorized
        
        # Add some common default categories
        defaults = [
            ("Social Media", "#e91e63", "📱"),
            ("Banking", "#4caf50", "🏦"),
            ("Work", "#2196f3", "💼"),
            ("Entertainment", "#ff9800", "🎬"),
            ("Shopping", "#9c27b0", "🛒"),
            ("Email", "#f44336", "📧")
        ]
        
        for name, color, icon in defaults:
            category = Category(name=name, color=color, icon=icon)
            self.categories[category.id] = category
    
    def create_category(self, name: str, color: str = "#6c757d", icon: str = "📁") -> Category:
        """Create a new category."""
        if not name.strip():
            raise ValueError("Category name cannot be empty")
        
        # Check for duplicate names (case-insensitive)
        if self._name_exists(name):
            raise ValueError(f"Category '{name}' already exists")
        
        # Validate color format
        if not self._is_valid_color(color):
            raise ValueError("Invalid color format")
        
        category = Category(name=name.strip(), color=color, icon=icon)
        self.categories[category.id] = category
        return category
    
    def update_category(self, category_id: str, name: str = None, color: str = None, icon: str = None) -> Category:
        """Update an existing category."""
        if category_id not in self.categories:
            raise ValueError(f"Category with ID '{category_id}' not found")
        
        # Cannot modify the uncategorized category name or delete it
        category = self.categories[category_id]
        if category_id == self.UNCATEGORIZED_ID and name is not None:
            raise ValueError("Cannot rename the Uncategorized category")
        
        if name is not None:
            name = name.strip()
            if not name:
                raise ValueError("Category name cannot be empty")
            if name != category.name and self._name_exists(name):
                raise ValueError(f"Category '{name}' already exists")
            category.name = name
        
        if color is not None:
            if not self._is_valid_color(color):
                raise ValueError("Invalid color format")
            category.color = color
        
        if icon is not None:
            category.icon = icon
        
        return category
    
    def delete_category(self, category_id: str) -> bool:
        """Delete a category. Cannot delete the uncategorized category."""
        if category_id == self.UNCATEGORIZED_ID:
            raise ValueError("Cannot delete the Uncategorized category")
        
        if category_id not in self.categories:
            return False
        
        del self.categories[category_id]
        return True
    
    def get_category(self, category_id: str) -> Optional[Category]:
        """Get a category by ID."""
        return self.categories.get(category_id)
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories, with Uncategorized first."""
        categories = list(self.categories.values())
        # Sort with Uncategorized first, then alphabetically
        categories.sort(key=lambda c: (c.id != self.UNCATEGORIZED_ID, c.name.lower()))
        return categories
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get a category by name (case-insensitive)."""
        for category in self.categories.values():
            if category.name.lower() == name.lower():
                return category
        return None
    
    def get_default_category(self) -> Category:
        """Get the default (uncategorized) category."""
        return self.categories[self.UNCATEGORIZED_ID]
    
    def _name_exists(self, name: str) -> bool:
        """Check if a category name already exists (case-insensitive)."""
        name_lower = name.lower()
        return any(cat.name.lower() == name_lower for cat in self.categories.values())
    
    def _is_valid_color(self, color: str) -> bool:
        """Validate hex color format."""
        if not color.startswith('#'):
            return False
        if len(color) not in [4, 7]:  # #RGB or #RRGGBB
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict:
        """Serialize categories to dictionary."""
        return {
            "categories": [cat.to_dict() for cat in self.categories.values()]
        }
    
    def from_dict(self, data: Dict):
        """Load categories from dictionary."""
        self.categories.clear()
        
        # Always ensure uncategorized exists
        if "categories" in data:
            for cat_data in data["categories"]:
                category = Category.from_dict(cat_data)
                self.categories[category.id] = category
        
        # Ensure uncategorized category exists
        if self.UNCATEGORIZED_ID not in self.categories:
            uncategorized = Category(
                id=self.UNCATEGORIZED_ID,
                name="Uncategorized",
                color="#6c757d",
                icon="📂"
            )
            self.categories[self.UNCATEGORIZED_ID] = uncategorized
    
    def count_entries_by_category(self, entries: List[Dict]) -> Dict[str, int]:
        """Count entries in each category."""
        counts = {cat_id: 0 for cat_id in self.categories.keys()}
        
        for entry in entries:
            category_id = entry.get("category", self.UNCATEGORIZED_ID)
            if category_id in counts:
                counts[category_id] += 1
            else:
                # Handle entries with invalid category IDs
                counts[self.UNCATEGORIZED_ID] += 1
        
        return counts
    
    def cleanup_entry_categories(self, entries: List[Dict]) -> List[Dict]:
        """Ensure all entries have valid category IDs."""
        for entry in entries:
            if "category" not in entry or entry["category"] not in self.categories:
                entry["category"] = self.UNCATEGORIZED_ID
        
        return entries

    @staticmethod
    def get_contrast_color(hex_color: str) -> str:
        """Get contrasting text color (black or white) for a background color."""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16) if len(hex_color) >= 2 else 0
        g = int(hex_color[2:4], 16) if len(hex_color) >= 4 else 0
        b = int(hex_color[4:6], 16) if len(hex_color) >= 6 else 0
        
        # Calculate relative luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Return black for light colors, white for dark colors
        return "#000000" if luminance > 0.5 else "#ffffff"
