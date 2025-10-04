#!/bin/bash
# PyVault Installation Script
# This script sets up PyVault for easy system-wide access

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories following Linux FHS (Filesystem Hierarchy Standard)
VAULT_DIR="$HOME/.pyvault"
PYVAULT_APP_DIR="$VAULT_DIR/app"  # Application files inside vault dir
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}     PyVault Installation       ${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to create directories
create_directories() {
    print_info "Creating necessary directories..."

    mkdir -p "$VAULT_DIR"
    mkdir -p "$PYVAULT_APP_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$ICON_DIR"

    # Secure vault directory permissions (includes app files)
    chmod 700 "$VAULT_DIR"    print_success "Directories created successfully"
}

# Function to install PyVault files
install_pyvault() {
    print_info "Installing PyVault application..."

    # Copy entire pyvault directory to ~/.pyvault/app/
    if [ -d "./dist/pyvault" ]; then
        cp -r ./dist/pyvault/* "$PYVAULT_APP_DIR/"
        chmod +x "$PYVAULT_APP_DIR/pyvault"
        print_success "PyVault files installed to $PYVAULT_APP_DIR"
    else
        print_error "PyVault build not found. Please run 'bash -c \"source venv/bin/activate && python -m PyInstaller --clean pyvault.spec\"' first"
        exit 1
    fi
}

# Function to create wrapper script
create_wrapper() {
    print_info "Creating launcher script..."

    cat > "$BIN_DIR/pyvault" << 'EOF'
#!/bin/bash
# PyVault Launcher Script
# Ensures consistent vault directory location

# Set working directory to home (vault will be in ~/.pyvault/)
cd "$HOME"

# Launch PyVault from ~/.pyvault/app/
exec "$HOME/.pyvault/app/pyvault" "$@"
EOF

    chmod +x "$BIN_DIR/pyvault"
    print_success "Launcher script created at $BIN_DIR/pyvault"
}

# Function to create desktop entry
create_desktop_entry() {
    print_info "Creating desktop entry..."

    cat > "$DESKTOP_DIR/pyvault.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PyVault
Comment=Secure Personal Password Manager
Comment[vi]=Trình Quản Lý Mật Khẩu Cá Nhân An Toàn
Exec=$HOME/.local/bin/pyvault
Icon=preferences-system-privacy
Path=$HOME
Terminal=false
Categories=Utility;Security;Office;
Keywords=password;security;vault;manager;
StartupWMClass=PyVault
EOF

    chmod +x "$DESKTOP_DIR/pyvault.desktop"
    print_success "Desktop entry created"
}

# Function to check PATH
check_path() {
    if echo "$PATH" | grep -q "$HOME/.local/bin"; then
        print_success "~/.local/bin is already in PATH"
    else
        print_warning "~/.local/bin is not in PATH"
        print_info "Add this line to your shell rc file (~/.bashrc, ~/.zshrc, etc.):"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

# Function to migrate existing vault
migrate_vault() {
    print_info "Checking for existing vault files..."

    # Look for vault.dat files
    VAULT_FILES=$(find "$HOME" -maxdepth 3 -name "vault.dat" -type f 2>/dev/null | head -5)

    if [ -n "$VAULT_FILES" ]; then
        print_warning "Found existing vault.dat files:"
        echo "$VAULT_FILES"

        echo -e "\n${YELLOW}Choose an option:${NC}"
        echo "1) Copy most recent vault.dat to ~/.pyvault/"
        echo "2) Skip migration (start fresh)"
        echo "3) Show file details to choose manually"

        read -p "Enter choice (1-3): " choice

        case $choice in
            1)
                LATEST_VAULT=$(echo "$VAULT_FILES" | xargs ls -t | head -n1)
                cp "$LATEST_VAULT" "$VAULT_DIR/vault.dat"
                print_success "Migrated vault from: $LATEST_VAULT"
                ;;
            2)
                print_info "Skipping vault migration"
                ;;
            3)
                echo "$VAULT_FILES" | xargs ls -la
                read -p "Enter full path to vault file to migrate (or press Enter to skip): " SELECTED_VAULT
                if [ -n "$SELECTED_VAULT" ] && [ -f "$SELECTED_VAULT" ]; then
                    cp "$SELECTED_VAULT" "$VAULT_DIR/vault.dat"
                    print_success "Migrated vault from: $SELECTED_VAULT"
                else
                    print_info "No vault migrated"
                fi
                ;;
            *)
                print_info "Invalid choice, skipping migration"
                ;;
        esac
    else
        print_info "No existing vault files found"
    fi
}

# Main installation function
main() {
    print_header

    create_directories
    install_pyvault
    create_wrapper
    create_desktop_entry
    check_path
    migrate_vault

    echo
    print_success "PyVault installation completed!"
    echo
    print_info "How to use:"
    echo "• Type 'pyvault' in terminal"
    echo "• Search 'PyVault' in application menu"
    echo "• Vault data will be stored in ~/.pyvault/vault.dat"
    echo "• Application files in ~/.pyvault/app/"
    echo
    print_info "To uninstall:"
    echo "rm -f '$BIN_DIR/pyvault' '$DESKTOP_DIR/pyvault.desktop'"
    echo "rm -rf '$VAULT_DIR'  # This will delete your password data AND app files!"
}

# Run main function
main "$@"
