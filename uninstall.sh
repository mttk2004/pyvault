#!/bin/bash
# PyVault Uninstallation Script
# This script safely removes PyVault from your system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Directories following Linux FHS
CONFIG_DIR="$HOME/.config/pyvault"           # User vault data (vault.dat)
PYVAULT_APP_DIR="$HOME/.local/share/pyvault" # Application files & assets
BIN_DIR="$HOME/.local/bin"                   # Executable launcher
DESKTOP_DIR="$HOME/.local/share/applications" # Desktop entries
PYVAULT_BIN="$BIN_DIR/pyvault"
DESKTOP_FILE="$DESKTOP_DIR/pyvault.desktop"

print_header() {
    echo -e "${MAGENTA}================================${NC}"
    echo -e "${MAGENTA}    PyVault Uninstallation      ${NC}"
    echo -e "${MAGENTA}================================${NC}"
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

print_critical() {
    echo -e "${RED}🚨 $1${NC}"
}

# Function to check if PyVault is installed
check_installation() {
    local components_found=0

    echo -e "\n${BLUE}Checking PyVault installation...${NC}"

    if [ -f "$PYVAULT_BIN" ]; then
        echo "• Launcher: Found at $PYVAULT_BIN"
        components_found=$((components_found + 1))
    else
        echo "• Launcher: Not found"
    fi

    if [ -d "$PYVAULT_APP_DIR" ]; then
        echo "• Application: Found at $PYVAULT_APP_DIR"
        components_found=$((components_found + 1))
    else
        echo "• Application: Not found"
    fi

    if [ -f "$DESKTOP_FILE" ]; then
        echo "• Desktop entry: Found at $DESKTOP_FILE"
        components_found=$((components_found + 1))
    else
        echo "• Desktop entry: Not found"
    fi

    if [ -d "$CONFIG_DIR" ]; then
        echo "• Vault data: Found at $CONFIG_DIR"
        if [ -f "$CONFIG_DIR/vault.dat" ]; then
            local vault_size=$(du -h "$CONFIG_DIR/vault.dat" 2>/dev/null | cut -f1)
            echo "  └── vault.dat: $vault_size (contains your password data)"
        fi
        components_found=$((components_found + 1))
    else
        echo "• Vault data: Not found"
    fi

    if [ $components_found -eq 0 ]; then
        print_error "PyVault is not installed or already removed"
        exit 0
    fi

    echo -e "\nFound $components_found PyVault component(s)"
}

# Function to stop running PyVault processes
stop_pyvault() {
    print_info "Stopping any running PyVault processes..."

    if pgrep -f "pyvault" > /dev/null 2>&1; then
        print_warning "Found running PyVault processes. Stopping them..."
        pkill -f "pyvault" 2>/dev/null || true
        sleep 1

        # Force kill if still running
        if pgrep -f "pyvault" > /dev/null 2>&1; then
            print_warning "Force stopping PyVault processes..."
            pkill -9 -f "pyvault" 2>/dev/null || true
        fi

        print_success "PyVault processes stopped"
    else
        print_info "No running PyVault processes found"
    fi
}

# Function to backup vault data
backup_vault_data() {
    if [ -f "$CONFIG_DIR/vault.dat" ]; then
        echo -e "\n${YELLOW}Your vault contains password data!${NC}"
        echo -e "${YELLOW}Do you want to create a backup before uninstalling?${NC}"
        echo "1) Yes, create backup in ~/Downloads/pyvault_backup_$(date +%Y%m%d_%H%M%S)/"
        echo "2) No, I have my own backup"
        echo "3) Cancel uninstallation"

        read -p "Enter choice (1-3): " backup_choice

        case $backup_choice in
            1)
                local backup_dir="$HOME/Downloads/pyvault_backup_$(date +%Y%m%d_%H%M%S)"
                mkdir -p "$backup_dir"
                cp -r "$CONFIG_DIR"/* "$backup_dir/"
                print_success "Vault data backed up to: $backup_dir"
                ;;
            2)
                print_info "Proceeding without creating backup"
                ;;
            3)
                print_info "Uninstallation cancelled by user"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Cancelling for safety."
                exit 1
                ;;
        esac
    fi
}

# Function to remove application files
remove_application() {
    print_info "Removing PyVault application files..."

    if [ -d "$PYVAULT_APP_DIR" ]; then
        local app_size=$(du -sh "$PYVAULT_APP_DIR" 2>/dev/null | cut -f1)
        rm -rf "$PYVAULT_APP_DIR"
        print_success "Removed application files ($app_size)"
    else
        print_info "Application files not found (already removed)"
    fi
}

# Function to remove launcher
remove_launcher() {
    print_info "Removing PyVault launcher..."

    if [ -f "$PYVAULT_BIN" ]; then
        rm -f "$PYVAULT_BIN"
        print_success "Removed launcher script"
    else
        print_info "Launcher script not found (already removed)"
    fi
}

# Function to remove desktop integration
remove_desktop_entry() {
    print_info "Removing desktop integration..."

    if [ -f "$DESKTOP_FILE" ]; then
        rm -f "$DESKTOP_FILE"
        print_success "Removed desktop entry"
    else
        print_info "Desktop entry not found (already removed)"
    fi

    # Update desktop database if available
    if command -v update-desktop-database > /dev/null 2>&1; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
}

# Function to handle vault data removal
remove_vault_data() {
    if [ -d "$CONFIG_DIR" ]; then
        echo -e "\n${RED}⚠️  CRITICAL DECISION ⚠️${NC}"
        echo -e "${RED}Do you want to delete your vault data (passwords)?${NC}"
        echo -e "${YELLOW}This action CANNOT be undone!${NC}"
        echo
        echo "• Your vault data is at: $CONFIG_DIR"
        if [ -f "$CONFIG_DIR/vault.dat" ]; then
            local vault_size=$(du -h "$CONFIG_DIR/vault.dat" 2>/dev/null | cut -f1)
            echo "• Size: $vault_size"
        fi
        echo
        echo "1) YES - Delete vault data (PERMANENT)"
        echo "2) NO - Keep vault data (you can reinstall PyVault later)"

        read -p "Enter choice (1-2): " data_choice

        case $data_choice in
            1)
                print_critical "Are you absolutely sure? Type 'DELETE' to confirm:"
                read -p "> " confirm
                if [ "$confirm" = "DELETE" ]; then
                    rm -rf "$CONFIG_DIR"
                    print_success "Vault data deleted permanently"
                else
                    print_info "Deletion cancelled. Vault data preserved."
                fi
                ;;
            2)
                print_info "Vault data preserved at: $CONFIG_DIR"
                print_info "You can reinstall PyVault later to access your passwords"
                ;;
            *)
                print_info "Invalid choice. Vault data preserved for safety."
                ;;
        esac
    else
        print_info "No vault data found"
    fi
}

# Function to clean up any leftover files
cleanup_leftovers() {
    print_info "Cleaning up any leftover files..."

    # Check for old installations
    local old_locations=(
        "$HOME/.pyvault"
        "$HOME/Applications/PyVault"
    )

    local found_old=false
    for location in "${old_locations[@]}"; do
        if [ -d "$location" ]; then
            echo -e "${YELLOW}Found old installation at: $location${NC}"
            read -p "Remove this old installation? (y/n): " remove_old
            if [[ "$remove_old" =~ ^[Yy] ]]; then
                rm -rf "$location"
                print_success "Removed old installation: $location"
            fi
            found_old=true
        fi
    done

    if [ "$found_old" = false ]; then
        print_info "No leftover files found"
    fi
}

# Function to show final status
show_final_status() {
    echo -e "\n${MAGENTA}================================${NC}"
    echo -e "${MAGENTA}    Uninstallation Summary      ${NC}"
    echo -e "${MAGENTA}================================${NC}"

    local status_color
    local status_icon

    # Check what remains
    echo -e "\n${BLUE}Component Status:${NC}"

    if [ -f "$PYVAULT_BIN" ]; then
        status_color="$YELLOW"
        status_icon="⚠️ "
    else
        status_color="$GREEN"
        status_icon="✅"
    fi
    echo -e "• Launcher: ${status_color}${status_icon} $([ -f "$PYVAULT_BIN" ] && echo "Still present" || echo "Removed")${NC}"

    if [ -d "$PYVAULT_APP_DIR" ]; then
        status_color="$YELLOW"
        status_icon="⚠️ "
    else
        status_color="$GREEN"
        status_icon="✅"
    fi
    echo -e "• Application: ${status_color}${status_icon} $([ -d "$PYVAULT_APP_DIR" ] && echo "Still present" || echo "Removed")${NC}"

    if [ -f "$DESKTOP_FILE" ]; then
        status_color="$YELLOW"
        status_icon="⚠️ "
    else
        status_color="$GREEN"
        status_icon="✅"
    fi
    echo -e "• Desktop entry: ${status_color}${status_icon} $([ -f "$DESKTOP_FILE" ] && echo "Still present" || echo "Removed")${NC}"

    if [ -d "$CONFIG_DIR" ]; then
        status_color="$BLUE"
        status_icon="💾"
        echo -e "• Vault data: ${status_color}${status_icon} Preserved at $CONFIG_DIR${NC}"
    else
        status_color="$RED"
        status_icon="🗑️ "
        echo -e "• Vault data: ${status_color}${status_icon} Deleted${NC}"
    fi

    echo -e "\n${GREEN}PyVault uninstallation completed!${NC}"

    if [ -d "$CONFIG_DIR" ]; then
        echo -e "\n${BLUE}Note: Your vault data is preserved.${NC}"
        echo -e "${BLUE}To reinstall: Download PyVault and run ./install.sh${NC}"
    fi
}

# Main uninstallation function
main() {
    print_header

    check_installation
    stop_pyvault
    backup_vault_data

    echo -e "\n${BLUE}Starting uninstallation...${NC}"

    remove_launcher
    remove_desktop_entry
    remove_application
    cleanup_leftovers
    remove_vault_data

    show_final_status
}

# Show help if requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "PyVault Uninstaller"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --force        Skip confirmations (keeps vault data)"
    echo
    echo "This script will:"
    echo "• Stop running PyVault processes"
    echo "• Remove application files from ~/.local/share/pyvault/"
    echo "• Remove launcher from ~/.local/bin/pyvault"
    echo "• Remove desktop entry"
    echo "• Optionally backup/remove vault data from ~/.config/pyvault/"
    echo
    echo "Your vault data will be preserved unless explicitly deleted."
    exit 0
fi

# Force mode (for automated uninstall)
if [[ "$1" == "--force" ]]; then
    print_header
    print_warning "Running in force mode (automated)"

    check_installation
    stop_pyvault
    remove_launcher
    remove_desktop_entry
    remove_application
    cleanup_leftovers

    print_success "PyVault application removed (vault data preserved)"
    print_info "Vault data preserved at: $CONFIG_DIR"
    exit 0
fi

# Run main function
main "$@"
