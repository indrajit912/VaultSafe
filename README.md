# Indrajit's Password Manager

## Overview

Indrajit's Password Manager is a command-line tool designed to securely manage credentials and sensitive information. It provides functionalities to initialize a password vault, add, retrieve, update, and delete credentials stored in the vault.

- **Author**: Indrajit Ghosh
- **Copyright**: © 2024 Indrajit Ghosh. All rights reserved.

## Installation

To install the app using a single terminal command, enter the following line:
```bash
curl -o ~/Downloads/install_password_manager.sh https://raw.githubusercontent.com/indrajit912/PasswordManager/master/scripts/install_password_manager.sh && chmod +x ~/Downloads/install_password_manager.sh && ~/Downloads/install_password_manager.sh
```
This command downloads the installation script to your ~/Downloads directory, makes it executable, and then runs it to install the password manager.

To uninstall the app using a single terminal command, enter the following line:
```bash
curl -o ~/Downloads/uninstall_password_manager.sh https://raw.githubusercontent.com/indrajit912/PasswordManager/master/scripts/uninstall_password_manager.sh && chmod +x ~/Downloads/uninstall_password_manager.sh && ~/Downloads/uninstall_password_manager.sh

```


### Using the Installation Script

To install the Password Manager application using the provided [install_password_manager.sh](./scripts/install_password_manager.sh) script, follow these steps:

1. **Download the Script:**

   [Click here](https://raw.githubusercontent.com/indrajit912/PasswordManager/master/scripts/install_password_manager.sh) to download `install_password_manager.sh` script to your computer.

2. **Make the Script Executable:**

   Open your terminal, navigate to the directory where you downloaded `install_password_manager.sh`, and make it executable:

   ```bash
   chmod +x install_password_manager.sh
   ```
3. Install the PasswordManager by the following command:
   ```bash
   ./install_password_manager.sh
   ```
4. Run the PasswordManager after restarting your terminal:
   ```bash
   password-manager help
   ```
5. Uninstall PasswordManager by the [uninstall_password_manager.sh](./scripts/uninstall_password_manager.sh) script. [Click here](https://raw.githubusercontent.com/indrajit912/PasswordManager/master/scripts/uninstall_password_manager.sh) to download that `uninstall_password_manager.sh` script.


## Command List

### init

Initialize the password vault.

This command sets up the password vault database if it doesn't already exist. If the database exists,
it provides an option to delete all existing data and start fresh.

**Notes:**
- The command initializes the database where credentials and vault information are stored.
- It prompts for the master password and optional vault attributes like name, owner name, and owner email.
- If the database already exists, it prompts to confirm deleting all existing data before reinitializing.

**Examples:**
To initialize the password vault:
```bash
password-manager init
```
---

### info

Display information about the password vault.

This command retrieves and displays the following information:
- Details about the currently initialized vault, including its name, owner, and creation timestamp.
- Total number of credentials stored in the vault.
- Total number of mnemonics associated with credentials in the vault.

**Notes:**
- The command requires the password vault to be initialized (`init` command) before use.
- It prints the vault information, total number of credentials, and total number of mnemonics.
- If no vault is found, it prompts the user to initialize the app using the `init` command first.

**Examples:**
To display information about the password vault:
```bash
password-manager info
```

---

### add

Add a new credential to the database.

**Args:**
- `name` (str): Name for the credential (required).
- `mnemonics` (list): Mnemonics associated with the credential (required, multiple values).
- `username` (str, optional): Username for the credential.
- `password` (str, optional): Password for the credential.
- `url` (str, optional): URL associated with the credential.

**Notes:**
- This command requires the database to be initialized ('init' command).
- Mnemonics provided must be unique and not already associated with other credentials.

**Examples:**
To add a credential with a name and mnemonics:
```bash
password-manager add -n "This is my Facebook Acc" -mn fb -mn facebook
```

To add a credential with all details (name, mnemonics, username, password, and URL):

```bash
password-manager add -n "My Credential Name" -mn mnemonic1 -mn mnemonic2 -u username -p password -url https://example.com
```

---

### get

Retrieve and display a credential from the database.

If 'mnemonic' is provided, display the credential associated with that mnemonic.
If 'mnemonic' is not provided, display all credentials stored in the vault.

**Args:**
- `mnemonic` (str, optional): The mnemonic associated with the credential to retrieve.

**Notes:**
- This command requires the database to be initialized ('init' command).

**Examples:**
To retrieve a credential by mnemonic:
```bash
password-manager get fb
```
To retrieve all credentials:
```bash
password-manager get
```


---

### update

Update an existing credential in the database.

This command allows updating various fields of a credential identified by either 'mnemonic' or 'uuid'.
At least one of these identifiers must be provided.

**Args:**
- `mnemonic` (str, optional): The mnemonic associated with the credential to update.
- `uuid` (str, optional): The UUID associated with the credential to update.
- `name` (str, optional): Updated name for the credential.
- `mnemonics` (list, optional): Updated mnemonics associated with the credential.
- `username` (str, optional): Updated username for the credential.
- `password` (str, optional): Updated password for the credential.
- `url` (str, optional): Updated URL for the credential.

**Notes:**
- If 'mnemonics' are provided, existing mnemonics associated with the credential will be replaced.
- The command requires the database to be initialized ('init' command).

**Examples:**
To update a credential by mnemonic:
```bash
password-manager update my_mnemonic -n "New Name" -u new_username # This will update only username
```
To update a credential by UUID:
```bash
password-manager update --uuid <UUID> -p new_password # This will update only the password; Use multiple flags such as:
password-manager update --uuid <UUID> -p new_password -u new_username
```

---
### open

Open a credential onto the browser from the database. If the password is saved for then the password will be copied to the clipboard.

**Args:**
- `mnemonic` (str, optional): The mnemonic associated with the credential to delete.

**Example:**
To open the credential with mnemonic `facebook` use:
```bash
password-manager open facebook
```
---

### delete

Delete a credential from the database.

**Args:**
- `mnemonic` (str, optional): The mnemonic associated with the credential to delete.

If 'mnemonic' is not provided as an argument, the user will be prompted to enter it interactively.

**Example:**
To delete the credential with mnemonic `facebook` use:
```bash
password-manager del facebook
```

---
### change-password
Command to change the master password for the password vault.

This command allows the user to change the master password used to encrypt and decrypt
credentials stored in the password vault.

**Example:**
To change the master password:
```bash
password-manager change-password
```

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.


