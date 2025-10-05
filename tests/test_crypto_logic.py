import unittest
import os
import sys

# Add the src directory to the Python path to import crypto_logic
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src import crypto_logic

class TestCryptoLogic(unittest.TestCase):

    def setUp(self):
        """Set up common variables for tests."""
        self.password = "my-super-secret-password-123"
        self.salt = os.urandom(crypto_logic.SALT_SIZE)
        self.plain_data = b'{"user": "test", "pass": "p@ssword"}'

    def test_derive_key_success(self):
        """Test that key derivation is successful with valid inputs."""
        key = crypto_logic.derive_key(self.password.encode(), self.salt)
        self.assertEqual(len(key), crypto_logic.KEY_SIZE)
        self.assertIsInstance(key, bytes)

        # Same password and salt should produce the same key
        key2 = crypto_logic.derive_key(self.password.encode(), self.salt)
        self.assertEqual(key, key2)

        # Different salt should produce a different key
        different_salt = os.urandom(crypto_logic.SALT_SIZE)
        key3 = crypto_logic.derive_key(self.password.encode(), different_salt)
        self.assertNotEqual(key, key3)

    def test_derive_key_invalid_input(self):
        """Test key derivation with invalid inputs."""
        with self.assertRaises(ValueError):
            crypto_logic.derive_key(b"", self.salt)  # Empty password
        with self.assertRaises(ValueError):
            crypto_logic.derive_key(self.password.encode(), b'')  # Empty salt
        with self.assertRaises(ValueError):
            crypto_logic.derive_key(self.password.encode(), os.urandom(8)) # Invalid salt size

    def test_encrypt_decrypt_roundtrip(self):
        """Test that data can be encrypted and then decrypted successfully."""
        key = crypto_logic.derive_key(self.password.encode(), self.salt)
        nonce, ciphertext = crypto_logic.encrypt(self.plain_data, key)

        self.assertEqual(len(nonce), crypto_logic.AES_NONCE_SIZE)
        self.assertNotEqual(self.plain_data, ciphertext)

        decrypted_data = crypto_logic.decrypt(nonce, ciphertext, key)
        self.assertEqual(self.plain_data, decrypted_data)

    def test_decrypt_wrong_key(self):
        """Test that decryption fails with the wrong key."""
        key1 = crypto_logic.derive_key(self.password.encode(), self.salt)
        nonce, ciphertext = crypto_logic.encrypt(self.plain_data, key1)

        wrong_password = "wrong-password"
        wrong_key = crypto_logic.derive_key(wrong_password.encode(), self.salt)

        with self.assertRaises(ValueError) as context:
            crypto_logic.decrypt(nonce, ciphertext, wrong_key)
        self.assertIn("Decryption failed", str(context.exception))


    def test_decrypt_tampered_data(self):
        """Test that decryption fails if the ciphertext is tampered with."""
        key = crypto_logic.derive_key(self.password.encode(), self.salt)
        nonce, ciphertext = crypto_logic.encrypt(self.plain_data, key)

        # Tamper with the ciphertext (flip a bit)
        tampered_ciphertext = bytearray(ciphertext)
        tampered_ciphertext[0] ^= 1

        with self.assertRaises(ValueError) as context:
            crypto_logic.decrypt(nonce, bytes(tampered_ciphertext), key)
        self.assertIn("Decryption failed", str(context.exception))

    def test_encrypt_invalid_input(self):
        """Test encryption with invalid inputs."""
        key = crypto_logic.derive_key(self.password.encode(), self.salt)
        with self.assertRaises(ValueError):
            crypto_logic.encrypt(b'', key) # Empty data
        with self.assertRaises(ValueError):
            crypto_logic.encrypt(self.plain_data, b'') # Empty key
        with self.assertRaises(ValueError):
            crypto_logic.encrypt(self.plain_data, os.urandom(16)) # Invalid key size

if __name__ == '__main__':
    unittest.main()
