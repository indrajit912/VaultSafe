# Password Manager CLI

Welcome to Indrajit's Password Manager, a command-line interface (CLI) tool for securely managing your credentials. This README provides an overview of the commands and usage instructions.

## Version
- Version: 1.0.0
- Copyright: © 2024 Indrajit Ghosh. All rights reserved.


## Table of Contents
- [Installation](#installation)
- [Initialization](#initialization)
- [Vault Information](#vault-information)
- [Password Generation](#password-generation)
- [Credential Management](#credential-management)
  - [Add Credential](#add-credential)
  - [Retrieve Credential](#retrieve-credential)
  - [Update Credential](#update-credential)
  - [Update Password](#update-password)
  - [Delete Credential](#delete-credential)
  - [Open Credential](#open-credential)
- [Master Password](#master-password)
- [Vault Management](#vault-management)
- [Import/Export](#importexport)
- [License](#license)

## Installation

To install and uninstall this on Linux/MacOS, use the provided shell scripts  [install_password_manager.sh](./scripts/install_password_manager.sh) and [uninstall_password_manager](./scripts/uninstall_password_manager.sh). Alternatively, you can run the following one-liners:

**Install**:
```sh
curl -o ~/Downloads/install_password_manager.sh https://raw.githubusercontent.com/indrajit912/PasswordManager/master/scripts/install_password_manager.sh && chmod +x ~/Downloads/install_password_manager.sh && ~/Downloads/install_password_manager.sh
```

**Uninstall**:
```sh
curl -o ~/Downloads/uninstall_password_manager.sh https://raw.githubusercontent.com/indrajit912/PasswordManager/master/scripts/uninstall_password_manager.sh && chmod +x ~/Downloads/uninstall_password_manager.sh && ~/Downloads/uninstall_password_manager.sh
```

Windows users can clone the repository to use the app.


## Commands

### Initialization

#### `init`
Initialize the password vault.

```sh
$ password-manager init
```
- Sets up the password vault database if it doesn't exist.
- Prompts for the master password and optional vault attributes (name, owner name, and owner email).
- If the database exists, confirms deleting existing data before reinitializing.

### Vault Information

#### `info`
Display information about the password vault.

```sh
$ password-manager info
```

### Password Generation

#### `generate`
Generate strong passwords of specified length.

Options:
- -l, --length (int): Length of the password to be generated. Default is 16.
- -c, --count (int): Number of passwords to generate. Default is 1.

Examples:
```sh
$ password-manager generate
$ password-manager generate --length 20
$ password-manager generate --length 20 --count 3
```

### Credential Management
#### Add Credential
#### `add`
Add a new credential to the database.

Options:
- -n, --name TEXT: Name for the credential (required).
- -mn, --mnemonics TEXT: Mnemonics associated with the credential (required, multiple values).
- -u, --username TEXT: Username for the credential (optional).
- -p, --password TEXT: Password for the credential (optional).
- -url, --url TEXT: URL associated with the credential (optional).

**Examples**:
```sh
$ password-manager add -n "My Credential Name" -mn mnemonic1 -mn mnemonic2
$ password-manager add -n "My Facebook Account" -mn fb -mn facebook -u username -p password -url https://example.com
```

### Retrieve Credential

#### `get`
Retrieve and display a credential from the database.

Args:
- mnemonic (str, optional): The mnemonic associated with the credential to retrieve.

**Examples**:
```sh
$ password-manager get my_mnemonic
$ password-manager get
```

### Update Credential

#### `update`
Update an existing credential in the database.

Options:
- -mnemonic (str, optional): Mnemonic identifier of the credential to update.
- --uuid TEXT: UUID associated with the credential to update.
- -n, --name TEXT: Updated name for the credential.
- -mn, --mnemonics TEXT: Updated mnemonics for the credential (can be specified multiple times).
- -u, --username TEXT: Updated username for the credential.
- -url, --url TEXT: Updated URL for the credential.

Examples:
```sh
$ password-manager update facebook -mn "new_mnemonic1" -mn "new_mnemonic2" -url "https://newurl.com"

$ password-manager update --uuid "123456" -n "New Credential Name" -u "new_username"

$ password-manager update twitter -n "Updated Name"
```

### Update Password

#### `update-password`
Update the password of an existing credential.

Args:
- mnemonic (str): The mnemonic identifier of the credential whose password is to be updated.

**Example**:
```sh
$ password-manager update-password my_mnemonic
```

### Delete Credential

#### `del`
Delete a credential from the database.

Args:
- mnemonic (str, optional): The mnemonic associated with the credential to delete.

Example:
```sh
$ password-manager del my_mnemonic
```

### Open Credential

#### `open`
Retrieve and display a credential from the database. If the credential's URL entry is not None, open the URL in a web browser.

Args:
- -mnemonic TEXT: Mnemonic of the credential to be opened.

**Example**:
```sh
$ password-manager open my_mnemonic
```

### Master Password

#### `change-master-password`
Change the master password for the password vault.

**Example**:
```sh
$ password-manager change-master-password
```

### Vault Management

#### `update-vault`
Update the vault information in the database.

Options:
- -n, --name TEXT: Update the name of the Vault.
- -o, --owner TEXT: Update the owner name for the Vault.
- -e, --email TEXT: Update the owner email for the Vault.

**Examples**:
```sh
$ password-manager update-vault -n "New Vault Name" -o "New Owner Name"
$ password-manager update-vault -e "newemail@example.com"
```

### Import/Export

#### `export`
Export credentials to a specified file format.

Options:
- -o, --output_dir (str): Directory where the exported file will be saved.
- -f, --file_format (str): File format for export ('json' or 'csv'). Defaults to 'json'.

**Example**:
```sh
$ password-manager export --output-dir /path/to/export --file-format csv
```

#### `import`
Import credentials from a JSON or CSV file into the database.

Arg:
- file_path (str): Path to the file containing credentials data.

Option:
- -f, --format (str): File format ('json' or 'csv').

**Example**:
```sh
$ password-manager import /path/to/credentials.csv --format csv
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
