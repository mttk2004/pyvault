# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

PyVault is a secure desktop password manager built with Python and PySide6. It uses military-grade AES-256-GCM encryption with PBKDF2 key derivation to protect user credentials locally. The application follows Linux FHS standards for file organization and supports cross-platform deployment.

## Architecture

### Core Components

**Security Layer (`src/crypto_logic.py`)**
- AES-256-GCM authenticated encryption for data protection
- PBKDF2-HMAC-SHA256 key derivation with 480,000 iterations
- Secure random salt and nonce generation
- All cryptographic operations use the `cryptography` library

**Storage Layer (`src/vault_manager.py`)**
- JSON-based vault file format with base64-encoded binary data
- Structure: `{"salt": "...", "nonce": "...", "ciphertext": "..."}`
- Custom exceptions: `VaultError`, `VaultNotFoundError`, `VaultCorruptedError`
- Secure file operations with proper error handling

**UI Layer (`src/ui/`)**
- `login_window.py`: Master password authentication interface
- `main_window.py`: Main password management interface  
- `entry_dialog.py`: Add/edit credential entry forms
- `styles.py`: Centralized styling and theming

**Application Controller (`main.py`)**
- PyVaultApp class manages application lifecycle
- Auto-lock functionality (5-minute inactivity timeout)
- Activity monitoring for security
- Vault file location: `~/.config/pyvault/vault.dat`

### Security Model

The application never stores the master password. Instead:
1. Master password + random salt → PBKDF2 → encryption key (in memory only)
2. User data → JSON → AES-GCM encryption → base64 → vault file
3. Authentication happens through successful decryption (GCM mode provides integrity)

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run from source
python main.py

# Run with Python path resolution
PYTHONPATH=. python main.py
```

### Testing
```bash
# Run all tests
python -m unittest discover tests/

# Run specific test modules
python -m unittest tests.test_crypto_logic
python -m unittest tests.test_vault_manager

# Run with verbose output
python -m unittest -v tests.test_crypto_logic.TestCryptoLogic.test_encrypt_decrypt_roundtrip
```

### Building and Distribution
```bash
# Install build dependencies
pip install pyinstaller

# Build executable
python -m PyInstaller --clean pyvault.spec

# Built application will be in dist/pyvault/
```

### Installation (Linux)
```bash
# Build first, then install
./install.sh

# Uninstall
./uninstall.sh
```

## File Structure Patterns

### Import Strategy
- `main.py` adds `src/` to Python path for absolute imports
- Test files add `../src` to path for importing modules
- UI modules use relative imports within the `ui` package

### Data Storage Locations
- **Development**: Vault file created in project directory during testing
- **Production**: `~/.config/pyvault/vault.dat` (Linux FHS compliant)
- **Application files**: `~/.local/share/pyvault/` when installed

### Test Data Management
- Tests use temporary files with `setUp()`/`tearDown()` cleanup
- Crypto tests use consistent test vectors for reproducibility
- Mock data generation uses `os.urandom()` for realistic byte sequences

## Common Development Patterns

### Crypto Operations
Always use the wrapper functions in `crypto_logic.py` rather than calling cryptography directly:
```python
# Correct
key = crypto_logic.derive_key(password.encode(), salt)
nonce, ciphertext = crypto_logic.encrypt(data, key)
decrypted = crypto_logic.decrypt(nonce, ciphertext, key)

# Avoid direct cryptography library calls
```

### Error Handling
Use custom vault exceptions for clear error semantics:
```python
try:
    salt, nonce, ciphertext = vault_manager.load_vault(file_path)
except VaultNotFoundError:
    # Handle new vault creation
except VaultCorruptedError:
    # Handle data corruption
```

### Qt Signal/Slot Pattern
The application uses Qt's signal/slot mechanism for loose coupling:
```python
# In UI components
self.unlocked.connect(self.handle_unlock)
self.data_changed.connect(self.handle_data_change)
```

## Security Considerations

- Master password is never stored or logged
- Encryption key exists only in memory during application runtime
- Auto-lock prevents unauthorized access during inactivity
- Vault directory permissions set to 700 (owner-only access)
- All user input is validated before cryptographic operations

## Dependencies

- **Python 3.10+**: Core runtime
- **PySide6**: Qt-based GUI framework
- **cryptography**: Cryptographic primitives and operations
- **PyInstaller**: Executable building (development only)
