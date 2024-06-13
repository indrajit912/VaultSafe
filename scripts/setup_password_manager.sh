#!/bin/bash

# Define variables
VENV_DIR="$HOME/pwmenv-$(date +%d-%m-%Y)"
REPO_URL="https://github.com/indrajit912/PasswordManager.git"
WRAPPER_SCRIPT="$HOME/bin/password-manager"

# Function to print messages
function print_message() {
    echo -e "\033[1;32m$1\033[0m"
}

# Step 1: Install virtualenv if not already installed
if ! command -v virtualenv &> /dev/null; then
    print_message "Installing virtualenv..."
    python3 -m pip install --user virtualenv
fi

# Step 2: Create a virtual environment
print_message "Creating virtual environment in $VENV_DIR..."
python3 -m virtualenv "$VENV_DIR"

# Step 3: Install the package inside the virtual environment
print_message "Installing password-manager from $REPO_URL..."
"$VENV_DIR/bin/python" -m pip install git+"$REPO_URL"

# Step 4: Create a wrapper script to activate the virtual environment and run the command
print_message "Creating wrapper script at $WRAPPER_SCRIPT..."
mkdir -p "$HOME/bin"
cat <<EOL > "$WRAPPER_SCRIPT"
#!/bin/bash
source "$VENV_DIR/bin/activate"
exec password-manager "\$@"
EOL
chmod +x "$WRAPPER_SCRIPT"

# Step 5: Ensure the wrapper script's directory is in the PATH
if ! grep -q 'export PATH=\$PATH:~/bin' "$HOME/.bashrc"; then
    print_message "Adding ~/bin to PATH in ~/.bashrc..."
    echo 'export PATH=$PATH:~/bin' >> "$HOME/.bashrc"
fi
if ! grep -q 'export PATH=\$PATH:~/bin' "$HOME/.zshrc"; then
    print_message "Adding ~/bin to PATH in ~/.zshrc..."
    echo 'export PATH=$PATH:~/bin' >> "$HOME/.zshrc"
fi

# Step 6: Install xclip
echo "Installing xclip..."
sudo apt-get install xclip

print_message "Setup complete! You can now use the 'password-manager' command."
print_message "Please restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to apply changes."
