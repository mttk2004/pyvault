import unittest
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.category_manager import CategoryManager, Category

class TestCategoryManager(unittest.TestCase):

    def setUp(self):
        """Set up a fresh CategoryManager for each test."""
        self.cm = CategoryManager()
        # Add a few initial categories for testing purposes
        self.cm.add_category("Social Media")
        self.cm.add_category("Banking")

    def test_default_category_exists(self):
        """Test that the 'Uncategorized' category always exists."""
        uncategorized = self.cm.categories.get(CategoryManager.UNCATEGORIZED_ID)
        self.assertIsNotNone(uncategorized)
        self.assertEqual(uncategorized.name, "Uncategorized")

    def test_add_category_success(self):
        """Test creating a new category successfully."""
        initial_count = len(self.cm.categories)
        category = self.cm.add_category("Work")
        self.assertEqual(category.name, "Work")
        self.assertEqual(len(self.cm.categories), initial_count + 1)

    def test_add_duplicate_category_fails(self):
        """Test that adding a duplicate category name (case-insensitive) fails."""
        with self.assertRaises(ValueError):
            self.cm.add_category("banking") # "Banking" already exists

    def test_add_empty_name_fails(self):
        """Test that adding a category with an empty name fails."""
        with self.assertRaises(ValueError):
            self.cm.add_category("   ")

    def test_update_category_success(self):
        """Test updating an existing category's name."""
        category = self.cm.add_category("To Be Updated")
        updated = self.cm.update_category(category.id, "Updated Name")
        self.assertEqual(updated.name, "Updated Name")
        self.assertEqual(self.cm.categories[category.id].name, "Updated Name")

    def test_cannot_rename_uncategorized(self):
        """Test that the 'Uncategorized' category cannot be renamed."""
        with self.assertRaises(ValueError):
            self.cm.update_category(CategoryManager.UNCATEGORIZED_ID, "New Name")

    def test_delete_category_success(self):
        """Test deleting a category."""
        category_to_delete = self.cm.add_category("To Delete")
        initial_count = len(self.cm.categories)
        
        self.cm.delete_category(category_to_delete.id)
        
        self.assertEqual(len(self.cm.categories), initial_count - 1)
        self.assertIsNone(self.cm.categories.get(category_to_delete.id))

    def test_cannot_delete_uncategorized(self):
        """Test that the 'Uncategorized' category cannot be deleted."""
        with self.assertRaises(ValueError):
            self.cm.delete_category(CategoryManager.UNCATEGORIZED_ID)

    def test_serialization_deserialization(self):
        """Test serializing all categories and deserializing them back."""
        data = self.cm.to_dict()
        
        new_cm = CategoryManager()
        new_cm.from_dict(data)
        
        self.assertEqual(len(new_cm.categories), len(self.cm.categories))
        original_names = sorted([c.name for c in self.cm.categories.values()])
        new_names = sorted([c.name for c in new_cm.categories.values()])
        self.assertListEqual(original_names, new_names)

    def test_get_category_helpers(self):
        """Test the helper methods for getting names and IDs."""
        names = self.cm.get_category_names()
        self.assertIn("Banking", names)
        self.assertIn("Uncategorized", names)

        banking_id = self.cm.get_category_id_by_name("Banking")
        self.assertIsNotNone(banking_id)
        
        banking_name = self.cm.get_category_name_by_id(banking_id)
        self.assertEqual(banking_name, "Banking")

if __name__ == '__main__':
    unittest.main()
