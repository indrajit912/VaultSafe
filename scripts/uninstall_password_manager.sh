#!/bin/bash

# Define variables
VENV_DIR_PATTERN="$HOME/pwmenv-*"
PASSWORD_MANAGER_DIR="$HOME/.password_manager"
WRAPPER_SCRIPT="$HOME/bin/password-manager"

# Function to print messages
function print_message() {
    echo -e "\033[1;31m$1\033[0m"
}

# Step 1: Remove all virtual environment directories matching the pattern
print_message "Removing virtual environment directories matching pattern: $VENV_DIR_PATTERN..."
rm -rf $VENV_DIR_PATTERN

# Step 2: Remove the password manager directory
if [ -d "$PASSWORD_MANAGER_DIR" ]; then
    print_message "Removing password manager directory: $PASSWORD_MANAGER_DIR..."
    rm -rf "$PASSWORD_MANAGER_DIR"
else
    print_message "Password manager directory does not exist: $PASSWORD_MANAGER_DIR"
fi

# Step 3: Remove the wrapper script
if [ -f "$WRAPPER_SCRIPT" ]; then
    print_message "Removing wrapper script: $WRAPPER_SCRIPT..."
    rm -f "$WRAPPER_SCRIPT"
else
    print_message "Wrapper script does not exist: $WRAPPER_SCRIPT"
fi

# Step 4: Remove the PATH addition from shell configuration files
if grep -q 'export PATH=\$PATH:~/bin' "$HOME/.bashrc"; then
    print_message "Removing PATH addition from ~/.bashrc..."
    sed -i '/export PATH=\$PATH:~\/bin/d' "$HOME/.bashrc"
fi
if grep -q 'export PATH=\$PATH:~/bin' "$HOME/.zshrc"; then
    print_message "Removing PATH addition from ~/.zshrc..."
    sed -i '/export PATH=\$PATH:~\/bin/d' "$HOME/.zshrc"
fi

print_message "Uninstallation complete! Please restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to apply changes."
