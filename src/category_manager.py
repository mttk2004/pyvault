"""
Category Management System for PyVault
Provides CRUD operations for password entry categories.
"""

import uuid
from typing import Dict, List, Optional

class Category:
    """Represents a password entry category."""
    
    def __init__(self, id: str = None, name: str = ""):
        self.id = id or str(uuid.uuid4())
        self.name = name
        
    def to_dict(self) -> Dict:
        return {"id": self.id, "name": self.name}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Category':
        return cls(id=data.get("id"), name=data.get("name", ""))

    def __str__(self):
        return self.name

class CategoryManager:
    """Manages categories for password entries."""
    
    UNCATEGORIZED_ID = "uncategorized"
    
    def __init__(self):
        self.categories: Dict[str, Category] = {}
        self._create_default_category()
        
    def _create_default_category(self):
        """Ensures the default 'Uncategorized' category always exists."""
        if self.UNCATEGORIZED_ID not in self.categories:
            uncategorized = Category(id=self.UNCATEGORIZED_ID, name="Uncategorized")
            self.categories[self.UNCATEGORIZED_ID] = uncategorized
    
    def add_category(self, name: str) -> Category:
        """Adds a new category."""
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty.")
        
        name = name.strip()
        if any(c.name.lower() == name.lower() for c in self.categories.values()):
            raise ValueError(f"Category '{name}' already exists.")

        new_cat = Category(name=name)
        self.categories[new_cat.id] = new_cat
        return new_cat

    def update_category(self, cat_id: str, new_name: str) -> Optional[Category]:
        """Updates an existing category's name."""
        if cat_id == self.UNCATEGORIZED_ID:
            raise ValueError("Cannot rename the 'Uncategorized' category.")

        category = self.categories.get(cat_id)
        if not category:
            return None

        new_name = new_name.strip()
        if any(c.name.lower() == new_name.lower() and c.id != cat_id for c in self.categories.values()):
            raise ValueError(f"Category name '{new_name}' already exists.")

        category.name = new_name
        return category

    def delete_category(self, cat_id: str):
        """Deletes a category."""
        if cat_id == self.UNCATEGORIZED_ID:
            raise ValueError("Cannot delete the 'Uncategorized' category.")
        if cat_id in self.categories:
            del self.categories[cat_id]

    def get_category_names(self) -> List[str]:
        """Returns a sorted list of category names."""
        names = [cat.name for cat in self.categories.values()]
        names.sort(key=lambda name: (name != "Uncategorized", name.lower()))
        return names

    def get_category_id_by_name(self, name: str) -> Optional[str]:
        """Finds a category ID by its name (case-insensitive)."""
        for cat_id, category in self.categories.items():
            if category.name.lower() == name.lower():
                return cat_id
        return None

    def get_category_name_by_id(self, cat_id: str) -> Optional[str]:
        """Finds a category name by its ID."""
        category = self.categories.get(cat_id)
        return category.name if category else None

    def to_dict(self) -> Dict:
        """Serializes all categories to a dictionary."""
        return { "categories": [cat.to_dict() for cat in self.categories.values()] }

    def from_dict(self, data: Dict):
        """Loads categories from a dictionary."""
        self.categories.clear()
        if "categories" in data:
            for cat_data in data["categories"]:
                category = Category.from_dict(cat_data)
                self.categories[category.id] = category
        self._create_default_category() # Ensure default always exists
    
    def cleanup_entry_categories(self, entries: List[dict]) -> List[dict]:
        """Assigns entries with invalid or missing categories to 'Uncategorized'."""
        valid_ids = set(self.categories.keys())
        for entry in entries:
            if entry.get("category_id") not in valid_ids:
                entry["category_id"] = self.UNCATEGORIZED_ID
        return entries
