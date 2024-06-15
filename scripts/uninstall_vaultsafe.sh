#!/bin/bash
#
# Uninstallation script for VaultSafe
#
# Author: Indrajit Ghosh
# Created On: Jun 14, 2024
#
# Usage: ./uninstall.sh [-f]
#   -f: Perform a full cleanup including removing the main directory and undoing PATH changes.
#
# This script performs the uninstallation of the vaultsafe CLI tool. 
# It supports both partial and full cleanup based on the command-line options.
# 
# Steps:
# 1. Parse command-line options for cleanup type.
# 2. Remove the virtual environment and/or the entire vaultsafe directory.
# 3. Remove any PATH additions which were added during installation from shell 
# configuration files (.bashrc, .zshrc, .bash_profile).
#
# Note: Make sure to restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc'
#       after uninstallation to apply all changes.
#

# Define variables
DOT_VAULTSAFE_DIR="$HOME/.vaultsafe"
VENV_DIR="$DOT_VAULTSAFE_DIR/pwmenv"
VAULTSAFE_ENV_BIN_DIR="$VENV_DIR/bin"

# Function to print messages
function print_message() {
    echo -e "\033[1;31m$1\033[0m"
}

# Step 1: Parse command-line options
if [[ "$1" == "-f" ]]; then
    # Perform full cleanup including undoing PATH changes
    if [ -d "$DOT_VAULTSAFE_DIR" ]; then
        print_message "Removing password manager directory: $DOT_VAULTSAFE_DIR..."
        rm -rf "$DOT_VAULTSAFE_DIR"
        echo "All source files related to vaultsafe have been deleted successfully."
    else
        print_message "No password manager directory found at: $DOT_VAULTSAFE_DIR"
    fi
else
    # Perform partial cleanup
    if ls -d $VENV_DIR &>/dev/null; then
        print_message "Removing virtual environment directory: $VENV_DIR..."
        rm -rf $VENV_DIR
        echo "Virtual environment directory removed successfully."
    else
        print_message "No virtual environment directory found: $VENV_DIR"
    fi
fi

# Step 2: Remove the PATH addition
# Remove the PATH addition from .bashrc if the file exists
if [ -f "$HOME/.bashrc" ]; then
    if grep -q "export PATH=\$PATH:$VAULTSAFE_ENV_BIN_DIR" "$HOME/.bashrc"; then
        print_message "Removing PATH addition from ~/.bashrc..."
        grep -v "export PATH=\$PATH:$VAULTSAFE_ENV_BIN_DIR" "$HOME/.bashrc" > "$HOME/.bashrc.tmp" && mv "$HOME/.bashrc.tmp" "$HOME/.bashrc"
    fi
else
    print_message "~/.bashrc file does not exist."
fi

# Remove the PATH addition from .zshrc if the file exists
if [ -f "$HOME/.zshrc" ]; then
    if grep -q "export PATH=\$PATH:$VAULTSAFE_ENV_BIN_DIR" "$HOME/.zshrc"; then
        print_message "Removing PATH addition from ~/.zshrc..."
        grep -v "export PATH=\$PATH:$VAULTSAFE_ENV_BIN_DIR" "$HOME/.zshrc" > "$HOME/.zshrc.tmp" && mv "$HOME/.zshrc.tmp" "$HOME/.zshrc"
    fi
else
    print_message "~/.zshrc file does not exist."
fi

# Remove the PATH addition from .bash_profile if the file exists
if [ -f "$HOME/.bash_profile" ]; then
    if grep -q "export PATH=\$PATH:$VAULTSAFE_ENV_BIN_DIR" "$HOME/.bash_profile"; then
        print_message "Removing PATH addition from ~/.bash_profile..."
        grep -v "export PATH=\$PATH:$VAULTSAFE_ENV_BIN_DIR" "$HOME/.bash_profile" > "$HOME/.bash_profile.tmp" && mv "$HOME/.bash_profile.tmp" "$HOME/.bash_profile"
    fi
else
    print_message "~/.bash_profile file does not exist."
fi

print_message "Uninstallation complete! Please restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to apply changes."
