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
  - [Delete Credential](#delete-credential)
  - [Open Credential](#open-credential)
- [Change Master Password](#change-master-password)
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
password-manager init
```
- Sets up the password vault database if it doesn't exist.
- Prompts for the master password and optional vault attributes (name, owner name, and owner email).
- If the database exists, confirms deleting existing data before reinitializing.

### Vault Information

#### `info`
Display information about the password vault.

```sh
password-manager info
```

### Password Generation

#### `generate`
Generate strong passwords of specified length.

**Options:**
- -l, --length (int): Length of the password to be generated. Default is 16.
- -c, --count (int): Number of passwords to generate. Default is 1.

**Examples:**
```sh
password-manager generate
password-manager generate --length 20
password-manager generate --length 20 --count 3
```

### Credential Management
#### Add Credential
#### `add`
Add a new credential to the database.

This command adds a new credential with various attributes to the password vault database.
It can add the name, mnemonics, username, primary email, secondary email, URL, and notes 
associated with the credential. The password, token, and recovery key can also be added 
using their respective flags.

**Options**:
- -n, --name TEXT: Name for the credential (required).
- -mn, --mnemonics TEXT: Mnemonics for the credential (can be specified multiple times) (required).
- -u, --username: Flag to add the username for the credential.
- -pw, --password: Flag to add the password.
- -rk, --recovery-key: Flag to add the recovery key.
- -url, --url: Flag to add the URL for the credential.
- -pe, --primary-email: Flag to add the primary email associated with the credential.
- -se, --secondary-email: Flag to add the secondary email associated with the credential.
- -tk, --token: Flag to add any token for the credential.
- -nt, --notes: Flag to add notes stored along with the credential.

**Examples**:
- Add a credential with name and mnemonics:
```sh
password-manager add -n "New Credential" -mn mnemonic1 -mn mnemonic2
```

- Add a credential with username and password:
```sh
password-manager add -n "New Credential" -mn mnemonic1 -u -pw
```

- Add a credential with primary and secondary emails:
```sh
password-manager add -n "New Credential" -mn mnemonic1 -pe -se
```

- Add a credential with URL and notes:
```sh
password-manager add -n "New Credential" -mn mnemonic1 -url -nt
```

- Add a credential with recovery key and token:
```sh
password-manager add -n "New Credential" -mn mnemonic1 -rk -tk
```

### Retrieve Credential

#### `get`
Retrieve and display a credential from the database.

Args:
- mnemonic (str, optional): The mnemonic associated with the credential to retrieve.

**Examples**:
- To retrieve a credential by mnemonic:
```sh
password-manager get my_mnemonic
```
- To retrieve all credentials:
```sh
password-manager get
```

### Update Credential

#### `update`
Update an existing credential in the database.

This command updates various attributes of a credential in the password vault database.
It can update the name, mnemonics, username, primary email, secondary email, URL, and notes 
associated with the credential. The password, token, and recovery key can also be updated 
using their respective flags.

**Argument:**
mnemonic (str, required): Mnemonic identifier of the credential to update.

**Options:**
- -n, --name: Flag to update the name for the credential.
- -mn, --mnemonics: Flag to update the mnemonics for the credential.
- -u, --username: Flag to update the username for the credential.
- -pw, --password: Flag to update the password.
- -tk, --token: Flag to update the token.
- -rk, --recovery-key: Flag to update the recovery key.
- -pe, --primary-email: Flag to update the primary email associated with the credential.
- -se, --secondary-email: Flag to update the secondary email associated with the credential.
- -url, --url: Flag to update the URL for the credential.
- -nt, --notes: Flag to update notes stored along with the credential.

**Examples:**
- Update the name and username of a credential:
```sh
password-manager update facebook -n -u
```

- Update mnemonics and URL for a credential whose mnemonic is 'twitter':
```sh
password-manager update twitter -mn -url
```

- Update only the name of a credential identified by mnemonic 'linkedin':
```sh
password-manager update linkedin -n
```

- Update primary and secondary emails for a credential:
```sh
password-manager update google -pe -se
```

- Update notes of a credential identified by mnemonic 'amazon':
```sh
password-manager update amazon -nt
```

- Update the password of a credential:
```sh
password-manager update microsoft -pw
```

- Update the token of a credential:
```sh
password-manager update github -tk
```

- Update the recovery key of a credential:
```sh
password-manager update dropbox -rk
```


### Delete Credential

#### `del`
Delete a credential from the database.

**Argument:**
- mnemonic (str, optional): The mnemonic associated with the credential to delete.

**Example:**
```sh
$ password-manager del my_mnemonic
```

### Open Credential

#### `open`
Retrieve and display a credential from the database. If the credential's URL entry is not None, open the URL in a web browser.

**Argument:**
- -mnemonic (str): Mnemonic of the credential to be opened.

**Example**:
```sh
password-manager open my_mnemonic
```

### Change Master Password

#### `change-master-password`
Change the master password for the password vault.

**Example**:
```sh
password-manager change-master-password
```

### Vault Management

#### `update-vault`
Update the vault information in the database.

**Options:**
- -n, --name TEXT: Update the name of the Vault.
- -o, --owner TEXT: Update the owner name for the Vault.
- -e, --email TEXT: Update the owner email for the Vault.

**Examples**:
```sh
password-manager update-vault -n "New Vault Name" -o "New Owner Name"
password-manager update-vault -e "newemail@example.com"
```

### Import/Export

#### `export`
Export credentials to a specified file format.

Options:
- -o, --output_dir (str): Directory where the exported file will be saved.
- -f, --file_format (str): File format for export ('json' or 'csv'). Defaults to 'json'.

**Example**:
```sh
password-manager export --output-dir /path/to/export --file-format csv
```

#### `import`
Import credentials from a JSON or CSV file into the database.

**Arg:**
- file_path (str): Path to the file containing credentials data.

**Option:**
- -f, --format (str): File format ('json' or 'csv').

**Example**:
```sh
password-manager import /path/to/credentials.csv --format csv
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
