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

    def test_default_categories_exist(self):
        """Test that default categories are created."""
        categories = self.cm.get_all_categories()
        self.assertGreater(len(categories), 0)
        
        # Check that uncategorized exists
        uncategorized = self.cm.get_default_category()
        self.assertEqual(uncategorized.name, "Uncategorized")
        self.assertEqual(uncategorized.id, CategoryManager.UNCATEGORIZED_ID)

    def test_create_category(self):
        """Test creating a new category."""
        initial_count = len(self.cm.get_all_categories())
        
        category = self.cm.create_category("Test Category", "#ff0000", "🧪")
        
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.color, "#ff0000")
        self.assertEqual(category.icon, "🧪")
        self.assertEqual(len(self.cm.get_all_categories()), initial_count + 1)

    def test_create_duplicate_category(self):
        """Test that creating duplicate categories fails."""
        self.cm.create_category("Test Category")
        
        with self.assertRaises(ValueError) as context:
            self.cm.create_category("Test Category")
        self.assertIn("already exists", str(context.exception))

    def test_update_category(self):
        """Test updating a category."""
        category = self.cm.create_category("Test Category", "#ff0000", "🧪")
        
        updated = self.cm.update_category(category.id, name="Updated Category", color="#00ff00", icon="✅")
        
        self.assertEqual(updated.name, "Updated Category")
        self.assertEqual(updated.color, "#00ff00")
        self.assertEqual(updated.icon, "✅")

    def test_cannot_rename_uncategorized(self):
        """Test that the uncategorized category cannot be renamed."""
        with self.assertRaises(ValueError):
            self.cm.update_category(CategoryManager.UNCATEGORIZED_ID, name="New Name")

    def test_delete_category(self):
        """Test deleting a category."""
        category = self.cm.create_category("Test Category")
        initial_count = len(self.cm.get_all_categories())
        
        success = self.cm.delete_category(category.id)
        
        self.assertTrue(success)
        self.assertEqual(len(self.cm.get_all_categories()), initial_count - 1)
        self.assertIsNone(self.cm.get_category(category.id))

    def test_cannot_delete_uncategorized(self):
        """Test that the uncategorized category cannot be deleted."""
        with self.assertRaises(ValueError):
            self.cm.delete_category(CategoryManager.UNCATEGORIZED_ID)

    def test_count_entries_by_category(self):
        """Test counting entries by category."""
        category1 = self.cm.create_category("Cat1")
        category2 = self.cm.create_category("Cat2")
        
        entries = [
            {"category": category1.id, "service": "test1"},
            {"category": category1.id, "service": "test2"},
            {"category": category2.id, "service": "test3"},
            {"category": CategoryManager.UNCATEGORIZED_ID, "service": "test4"},
            {"service": "test5"}  # No category field
        ]
        
        counts = self.cm.count_entries_by_category(entries)
        
        self.assertEqual(counts[category1.id], 2)
        self.assertEqual(counts[category2.id], 1)
        self.assertEqual(counts[CategoryManager.UNCATEGORIZED_ID], 2)  # includes entry without category field

    def test_cleanup_entry_categories(self):
        """Test cleaning up entries with invalid categories."""
        category = self.cm.create_category("Valid Category")
        
        entries = [
            {"category": category.id, "service": "test1"},
            {"category": "invalid_id", "service": "test2"},
            {"service": "test3"}  # No category field
        ]
        
        cleaned = self.cm.cleanup_entry_categories(entries)
        
        self.assertEqual(cleaned[0]["category"], category.id)
        self.assertEqual(cleaned[1]["category"], CategoryManager.UNCATEGORIZED_ID)
        self.assertEqual(cleaned[2]["category"], CategoryManager.UNCATEGORIZED_ID)

    def test_serialization(self):
        """Test serializing and deserializing categories."""
        # Create some categories
        cat1 = self.cm.create_category("Cat1", "#ff0000", "🧪")
        cat2 = self.cm.create_category("Cat2", "#00ff00", "🔧")
        
        # Serialize
        data = self.cm.to_dict()
        
        # Create new manager and deserialize
        new_cm = CategoryManager()
        new_cm.from_dict(data)
        
        # Verify categories exist
        self.assertEqual(len(new_cm.get_all_categories()), len(self.cm.get_all_categories()))
        
        new_cat1 = new_cm.get_category(cat1.id)
        self.assertIsNotNone(new_cat1)
        self.assertEqual(new_cat1.name, "Cat1")
        self.assertEqual(new_cat1.color, "#ff0000")
        self.assertEqual(new_cat1.icon, "🧪")

    def test_color_validation(self):
        """Test color validation."""
        # Valid colors
        self.cm.create_category("Test1", "#ff0000")
        self.cm.create_category("Test2", "#abc")
        
        # Invalid colors
        with self.assertRaises(ValueError):
            self.cm.create_category("Test3", "ff0000")  # Missing #
        with self.assertRaises(ValueError):
            self.cm.create_category("Test4", "#gggggg")  # Invalid hex

    def test_contrast_color(self):
        """Test contrast color calculation."""
        # Light color should return black text
        self.assertEqual(CategoryManager.get_contrast_color("#ffffff"), "#000000")
        
        # Dark color should return white text
        self.assertEqual(CategoryManager.get_contrast_color("#000000"), "#ffffff")

if __name__ == '__main__':
    unittest.main()
