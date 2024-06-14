#!/bin/bash
#
# Installation script for Password Manager application
#
# Author: Indrajit Ghosh
# Created On: Jun 14, 2024
#
# This script will install the Password Manager application by performing the following steps:
#
# 1. Check if Python 3.6 or higher is installed.
# 2. Create necessary directories and virtual environment.
# 3. Install dependencies and the Password Manager application.
# 4. Create a wrapper script for easy command execution.
# 5. Add the necessary directories to PATH in ~/.bashrc, ~/.zshrc, or ~/.bash_profile.
# 6. Install xclip if not already installed (used for clipboard functionality).
#
# Note: Make sure to restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc'
#       after installation to apply all changes.
#

# Function to print messages
function print_message() {
    echo -e "\033[1;32m$1\033[0m"
}

# Step 1: Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: 'password_manager' requires Python version >= 3.6. Please install Python 3.6 or higher and try again."
    exit 1
fi

# Step 2: Check if python3 version is >= 3.6
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
REQUIRED_VERSION="3.6"

if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo "Error: 'password_manager' requires Python version >= 3.6. Installed version is $PYTHON_VERSION. Please upgrade your Python version."
    exit 1
fi

# Define variables
DOT_PASSWD_MGR_DIR="$HOME/.password_manager"
VENV_DIR="$DOT_PASSWD_MGR_DIR/pwmenv"
PASSWD_MGR_ENV_BIN_DIR="$VENV_DIR/bin"
REPO_URL="https://github.com/indrajit912/PasswordManager.git"

# Step 3: Ensure the base directory exists
if [ ! -d "$DOT_PASSWD_MGR_DIR" ]; then
    print_message "Creating base directory $DOT_PASSWD_MGR_DIR..."
    mkdir -p "$DOT_PASSWD_MGR_DIR"
fi

# Step 4: Install virtualenv if not already installed
if ! command -v virtualenv &> /dev/null; then
    print_message "Installing virtualenv..."
    python3 -m pip install --user virtualenv
fi

# Step 5: Create a virtual environment
print_message "Creating virtual environment in $VENV_DIR..."
python3 -m virtualenv "$VENV_DIR"


# Step 6: Install the package inside the virtual environment
print_message "Installing password-manager from $REPO_URL..."
"$VENV_DIR/bin/python" -m pip install git+"$REPO_URL"


# Check and update .bashrc
if [ -f "$HOME/.bashrc" ]; then
    if ! grep -q "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" "$HOME/.bashrc"; then
        print_message "Adding $PASSWD_MGR_ENV_BIN_DIR to PATH in ~/.bashrc..."
        echo "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" >> "$HOME/.bashrc"
    fi
else
    print_message "~/.bashrc file does not exist."
fi

# Check and update .zshrc
if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" "$HOME/.zshrc"; then
        print_message "Adding $PASSWD_MGR_ENV_BIN_DIR to PATH in ~/.zshrc..."
        echo "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" >> "$HOME/.zshrc"
    fi
else
    print_message "~/.zshrc file does not exist."
fi

# Check and update .bash_profile
if [ -f "$HOME/.bash_profile" ]; then
    if ! grep -q "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" "$HOME/.bash_profile"; then
        print_message "Adding $PASSWD_MGR_ENV_BIN_DIR to PATH in ~/.bash_profile..."
        echo "export PATH=\$PATH:$PASSWD_MGR_ENV_BIN_DIR" >> "$HOME/.bash_profile"
    fi
else
    print_message "~/.bash_profile file does not exist."
fi

# Step 9: Check if xclip is installed, if not, install it
if ! command -v xclip &> /dev/null; then
    print_message "Installing xclip..."
    sudo apt-get install xclip
else
    print_message "xclip is already installed."
fi

print_message "Setup complete! You can now use the 'password-manager' command."
print_message "Please restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to apply changes."