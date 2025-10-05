import unittest
import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src import vault_manager

class TestVaultManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary file path for testing."""
        self.test_file = "test_vault.dat"
        self.salt = os.urandom(16)
        self.nonce = os.urandom(12)
        self.ciphertext = os.urandom(32)

    def tearDown(self):
        """Clean up the test file after each test."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_and_load_vault_roundtrip(self):
        """Test that saving and loading a vault works correctly."""
        vault_manager.save_vault(self.test_file, self.salt, self.nonce, self.ciphertext)

        self.assertTrue(os.path.exists(self.test_file))

        loaded_salt, loaded_nonce, loaded_ciphertext = vault_manager.load_vault(self.test_file)

        self.assertEqual(self.salt, loaded_salt)
        self.assertEqual(self.nonce, loaded_nonce)
        self.assertEqual(self.ciphertext, loaded_ciphertext)

    def test_load_vault_not_found(self):
        """Test that loading a non-existent vault raises VaultNotFoundError."""
        with self.assertRaises(vault_manager.VaultNotFoundError):
            vault_manager.load_vault("non_existent_file.dat")

    def test_load_vault_corrupted_json(self):
        """Test that loading a vault with invalid JSON raises VaultCorruptedError."""
        with open(self.test_file, 'w') as f:
            f.write("{ not json }")

        with self.assertRaises(vault_manager.VaultCorruptedError):
            vault_manager.load_vault(self.test_file)

    def test_load_vault_missing_keys(self):
        """Test that loading a vault with missing keys raises VaultCorruptedError."""
        corrupted_data = {
            "salt": "c2FsdA==",
            "ciphertext": "Y2lwaGVydGV4dA=="
            # "nonce" is missing
        }
        with open(self.test_file, 'w') as f:
            json.dump(corrupted_data, f)

        with self.assertRaises(vault_manager.VaultCorruptedError):
            vault_manager.load_vault(self.test_file)

    def test_load_vault_invalid_base64(self):
        """Test that loading a vault with invalid base64 data raises VaultCorruptedError."""
        corrupted_data = {
            "salt": "c2FsdA==",
            "nonce": "invalid-base64", # This is not a valid base64 string
            "ciphertext": "Y2lwaGVydGV4dA=="
        }
        with open(self.test_file, 'w') as f:
            json.dump(corrupted_data, f)

        with self.assertRaises(vault_manager.VaultCorruptedError):
            vault_manager.load_vault(self.test_file)

    def test_save_vault_empty_parameters(self):
        """Test that save_vault raises ValueError for empty parameters."""
        with self.assertRaises(ValueError):
            vault_manager.save_vault("", self.salt, self.nonce, self.ciphertext)
        with self.assertRaises(ValueError):
            vault_manager.save_vault(self.test_file, b"", self.nonce, self.ciphertext)

if __name__ == '__main__':
    unittest.main()
