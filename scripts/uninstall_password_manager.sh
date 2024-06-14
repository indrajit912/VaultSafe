#!/bin/bash
#
# Uninstallation script for Password Manager application
#
# Author: Indrajit Ghosh
# Created On: Jun 14, 2024
#
# Usage: ./uninstall.sh [-f]
#   -f: Perform a full cleanup including removing the main directory and undoing PATH changes.
#
# This script will uninstall the Password Manager application by removing:
# - Virtual environment directories created during installation.
# - Password manager binary directory and associated wrapper script.
# - Optionally, undo changes made to PATH variables in shell configuration files.
#
# Note: Make sure to restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc'
#       after uninstallation to apply all changes.
#

# Define variables
DOT_PASSWD_MGR_DIR="$HOME/.password_manager"
VENV_DIR="$DOT_PASSWD_MGR_DIR/pwmenv"
PASSWD_MGR_ENV_BIN_DIR="$VENV_DIR/bin"

# Function to print messages
function print_message() {
    echo -e "\033[1;31m$1\033[0m"
}

# Step 1: Parse command-line options
if [[ "$1" == "-f" ]]; then
    # Perform full cleanup including undoing PATH changes
    if [ -d "$DOT_PASSWD_MGR_DIR" ]; then
        print_message "Removing password manager directory: $DOT_PASSWD_MGR_DIR..."
        rm -rf "$DOT_PASSWD_MGR_DIR"
        echo "All source files related to password_manager have been deleted successfully."
    else
        print_message "No password manager directory found at: $DOT_PASSWD_MGR_DIR"
    fi
else
    # Perform partial cleanup
    if ls -d $VENV_DIR_PATTERN &>/dev/null; then
        print_message "Removing virtual environment directories matching pattern: $VENV_DIR_PATTERN..."
        rm -rf $VENV_DIR_PATTERN
        echo "Virtual environment directories removed successfully."
    else
        print_message "No virtual environment directories found matching pattern: $VENV_DIR_PATTERN"
    fi
fi

# Remove the PATH addition from .bashrc if the file exists
if [ -f "$HOME/.bashrc" ]; then
    if grep -q "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" "$HOME/.bashrc"; then
        print_message "Removing PATH addition from ~/.bashrc..."
        sed -i "\|export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR|d" "$HOME/.bashrc"
    fi
else
    print_message "~/.bashrc file does not exist."
fi

# Remove the PATH addition from .zshrc if the file exists
if [ -f "$HOME/.zshrc" ]; then
    if grep -q "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" "$HOME/.zshrc"; then
        print_message "Removing PATH addition from ~/.zshrc..."
        sed -i "\|export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR|d" "$HOME/.zshrc"
    fi
else
    print_message "~/.zshrc file does not exist."
fi

# Remove the PATH addition from .bash_profile if the file exists
if [ -f "$HOME/.bash_profile" ]; then
    if grep -q "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" "$HOME/.bash_profile"; then
        print_message "Removing PATH addition from ~/.bash_profile..."
        sed -i "\|export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR|d" "$HOME/.bash_profile"
    fi
else
    print_message "~/.bash_profile file does not exist."
fi

print_message "Uninstallation complete! Please restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to apply changes."
