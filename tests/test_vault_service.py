# tests/test_vault_service.py
import unittest
from unittest.mock import patch, MagicMock

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.services.vault_service import VaultService
from src.models.vault import Vault
from src.models.credential_entry import CredentialEntry

# Since we are testing VaultService in isolation, we don't need real crypto or file access.
# We will mock these dependencies.

class TestVaultService(unittest.TestCase):

    @patch('src.services.vault_service.os.path.exists')
    def setUp(self, mock_exists):
        """Set up a fresh VaultService instance for each test."""
        # By default, simulate that the vault does not exist
        mock_exists.return_value = False
        self.service = VaultService()
        self.password = "test-password"

    @patch('src.services.vault_service.os.path.exists')
    def test_init_vault_exists(self, mock_exists):
        """Test that vault_exists is True if the file is found."""
        mock_exists.return_value = True
        service = VaultService()
        self.assertTrue(service.vault_exists)

    @patch('src.services.vault_service.os.path.exists')
    def test_init_vault_does_not_exist(self, mock_exists):
        """Test that vault_exists is False if the file is not found."""
        mock_exists.return_value = False
        service = VaultService()
        self.assertFalse(service.vault_exists)

    @patch('src.services.vault_service.vault_manager.save_vault')
    @patch('src.services.vault_service.crypto_logic.encrypt')
    @patch('src.services.vault_service.crypto_logic.derive_key')
    @patch('src.services.vault_service.crypto_logic.generate_salt')
    def test_create_vault_success(self, mock_generate_salt, mock_derive_key, mock_encrypt, mock_save_vault):
        """Test the successful creation of a new vault."""
        # Arrange: Mock the return values of crypto functions
        mock_generate_salt.return_value = b'salt' * 4
        mock_derive_key.return_value = b'key' * 8
        mock_encrypt.return_value = (b'nonce' * 3, b'ciphertext')

        # Act
        success, message, vault = self.service.unlock_or_create(self.password)

        # Assert
        self.assertTrue(success)
        self.assertIn("Vault created successfully", message)
        self.assertIsInstance(vault, Vault)
        self.assertEqual(len(vault.entries), 0)

        # Verify that our mocks were called correctly
        mock_generate_salt.assert_called_once()
        mock_derive_key.assert_called_once_with(self.password.encode(), b'salt' * 4)
        mock_encrypt.assert_called_once()
        mock_save_vault.assert_called_once()

    @patch('src.services.vault_service.crypto_logic.decrypt')
    @patch('src.services.vault_service.crypto_logic.derive_key')
    @patch('src.services.vault_service.vault_manager.load_vault')
    @patch('src.services.vault_service.os.path.exists')
    def test_unlock_vault_success(self, mock_exists, mock_load_vault, mock_derive_key, mock_decrypt):
        """Test successfully unlocking an existing vault."""
        # Arrange
        mock_exists.return_value = True
        self.service = VaultService() # Re-initialize with vault existing

        mock_load_vault.return_value = (b'salt' * 4, b'nonce' * 3, b'ciphertext')
        mock_derive_key.return_value = b'key' * 8

        # Mock decrypted data to be a valid JSON structure for a Vault
        decrypted_json = '{"entries": [{"service": "test"}], "categories": {}}'
        mock_decrypt.return_value = decrypted_json.encode('utf-8')

        # Act
        success, message, vault = self.service.unlock_or_create(self.password)

        # Assert
        self.assertTrue(success)
        self.assertEqual(message, "")
        self.assertIsInstance(vault, Vault)
        self.assertEqual(len(vault.entries), 1)
        self.assertEqual(vault.entries[0].service, "test")

        mock_load_vault.assert_called_once()
        mock_decrypt.assert_called_once_with(b'nonce' * 3, b'ciphertext', b'key' * 8)

    @patch('src.services.vault_service.crypto_logic.decrypt')
    @patch('src.services.vault_service.crypto_logic.derive_key')
    @patch('src.services.vault_service.vault_manager.load_vault')
    @patch('src.services.vault_service.os.path.exists')
    def test_unlock_vault_failure_wrong_password(self, mock_exists, mock_load_vault, mock_derive_key, mock_decrypt):
        """Test failure when unlocking with an incorrect password."""
        # Arrange
        mock_exists.return_value = True
        self.service = VaultService()

        mock_load_vault.return_value = (b'salt' * 4, b'nonce' * 3, b'ciphertext')
        mock_derive_key.return_value = b'wrong_key' * 4
        # Simulate decryption failure by raising a ValueError
        mock_decrypt.side_effect = ValueError("Decryption failed. Incorrect password or corrupted data.")

        # Act
        success, message, vault = self.service.unlock_or_create(self.password)

        # Assert
        self.assertFalse(success)
        self.assertIn("Decryption failed", message)
        self.assertIsNone(vault)

    def test_lock(self):
        """Test that locking the vault resets its state."""
        # Arrange: first, put the service in an "unlocked" state
        self.service.key = b'some-key'
        self.service.vault = Vault()

        # Act
        self.service.lock()

        # Assert
        self.assertIsNone(self.service.key)
        self.assertIsNone(self.service.vault)

if __name__ == '__main__':
    unittest.main()
