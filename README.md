# VaultSafe

Welcome to VaultSafe, a robust and user-friendly command-line application designed to manage your credentials with the highest level of security. This app ensures that your sensitive information is protected using state-of-the-art encryption algorithms, providing end-to-end encryption to keep your data safe from prying eyes.

**Key Features:**

- **Add Credentials:** Easily add new credentials to your secure vault with multiple options such as `--token`, `--recovery-key`, `--primary-email` etc.
- **Get Credentials:** Retrieve your stored credentials effortlessly using your `master_password`.
- **Update Credentials:** Modify existing credentials securely.
- **Delete Credentials:** Remove credentials that you no longer need with ease.
- **Export Data:** Export your encrypted credentials in JSON or CSV format for backup or transfer purposes.
- **Import Data:** Import exported credentials into the app seamlessly.

**Security Highlights:**

- **End-to-End Encryption:** All credential data is encrypted with a very strong encryption algorithm, ensuring that it remains secure from the moment you input it.
- **Master Password Protection:** Your credentials can only be decrypted using a master password that you create and remember. Without this password, decryption is mathematically impossible, ensuring that only you have access to your data.

**Usage:**
The VaultSafe CLI is designed to be intuitive and easy to use, providing you with a simple yet powerful tool to manage your credentials securely. Whether you're adding a new set of credentials, updating existing ones, or exporting your data for safekeeping, this app provides all the functionalities you need in a straightforward command-line interface.

**Contact:**
For any issues, feature requests, or contributions, please reach out via the GitHub repository. Your feedback is highly valued and helps improve the app.

Secure your credentials with confidence using the Secure Credentials Manager CLI, and rest assured that your sensitive information is protected by the highest standards of encryption.

---

**Repository:** [GitHub Link](https://github.com/indrajit912/VaultSafe.git)

**Developer:** [Indrajit Ghosh](https://indrajitghosh.onrender.com), SRF, Stat-Math Unit, Indian Statistical Institute, Bangalore


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

To install and uninstall this on Linux/MacOS, use the provided shell scripts  [install_vaultsafe.sh](./scripts/install_vaultsafe.sh) and [uninstall_vaultsafe](./scripts/uninstall_vaultsafe.sh). Alternatively, you can run the following one-liners:

**Install**:
```sh
curl -o ~/Downloads/install_vaultsafe.sh https://raw.githubusercontent.com/indrajit912/VaultSafe/master/scripts/install_vaultsafe.sh && chmod +x ~/Downloads/install_vaultsafe.sh && ~/Downloads/install_vaultsafe.sh
```

**Uninstall**:
```sh
curl -o ~/Downloads/uninstall_vaultsafe.sh https://raw.githubusercontent.com/indrajit912/VaultSafe/master/scripts/uninstall_vaultsafe.sh && chmod +x ~/Downloads/uninstall_vaultsafe.sh && ~/Downloads/uninstall_vaultsafe.sh
```

### Installation Instructions for Windows

1. **Ensure Python >= 3.6 is Installed:**
   - Check if Python is installed by opening a command prompt (`cmd`) and typing:
     ```cmd
     python --version
     ```
     If Python is not installed or the version is below 3.6, download and install Python from [python.org](https://www.python.org/downloads/).

2. **Install virtualenv:**
   - Open a command prompt (`cmd`) and install `virtualenv` using pip:
     ```cmd
     pip install virtualenv
     ```

3. **Clone the Repository and Install VaultSafe:**
   - Open a command prompt (`cmd`) and navigate to the directory where you want to install the app.

   - Create a virtual environment:
     ```cmd
     virtualenv venv
     ```
     Activate the virtual environment:
     ```cmd
     venv\Scripts\activate
     ```

   - Install the VaultSafe package from the cloned repository:
     ```cmd
     pip install git+https://github.com/indrajit912/VaultSafe.git

     ```

   This will install the VaultSafe application and its dependencies into the virtual environment.

### Usage

- To run the VaultSafe application after installation, ensure your virtual environment is activated (`venv\Scripts\activate` in the command prompt), then you can start the application by the command:
  ```cmd
  vaultsafe help
  ```


## Commands

### Initialization

#### `init`
Initialize the password vault.

```sh
vaultsafe init
```
- Sets up the password vault database if it doesn't exist.
- Prompts for the master password and optional vault attributes (name, owner name, and owner email).
- If the database exists, confirms deleting existing data before reinitializing.

### Vault Information

#### `info`
Display information about the password vault.

```sh
vaultsafe info
```

### Password Generation

#### `generate`
Generate strong passwords of specified length.

**Options:**
- -l, --length (int): Length of the password to be generated. Default is 16.
- -c, --count (int): Number of passwords to generate. Default is 1.

**Examples:**
```sh
vaultsafe generate
vaultsafe generate --length 20
vaultsafe generate --length 20 --count 3
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
vaultsafe add -n "New Credential" -mn mnemonic1 -mn mnemonic2
```

- Add a credential with username and password:
```sh
vaultsafe add -n "New Credential" -mn mnemonic1 -u -pw
```

- Add a credential with primary and secondary emails:
```sh
vaultsafe add -n "New Credential" -mn mnemonic1 -pe -se
```

- Add a credential with URL and notes:
```sh
vaultsafe add -n "New Credential" -mn mnemonic1 -url -nt
```

- Add a credential with recovery key and token:
```sh
vaultsafe add -n "New Credential" -mn mnemonic1 -rk -tk
```

### Retrieve Credential

#### `get`
Retrieve and display a credential from the database.

Args:
- mnemonic (str, optional): The mnemonic associated with the credential to retrieve.

**Examples**:
- To retrieve a credential by mnemonic:
```sh
vaultsafe get my_mnemonic
```
- To retrieve all credentials:
```sh
vaultsafe get
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
vaultsafe update facebook -n -u
```

- Update mnemonics and URL for a credential whose mnemonic is 'twitter':
```sh
vaultsafe update twitter -mn -url
```

- Update only the name of a credential identified by mnemonic 'linkedin':
```sh
vaultsafe update linkedin -n
```

- Update primary and secondary emails for a credential:
```sh
vaultsafe update google -pe -se
```

- Update notes of a credential identified by mnemonic 'amazon':
```sh
vaultsafe update amazon -nt
```

- Update the password of a credential:
```sh
vaultsafe update microsoft -pw
```

- Update the token of a credential:
```sh
vaultsafe update github -tk
```

- Update the recovery key of a credential:
```sh
vaultsafe update dropbox -rk
```


### Delete Credential

#### `del`
Delete a credential from the database.

**Argument:**
- mnemonic (str, optional): The mnemonic associated with the credential to delete.

**Example:**
```sh
$ vaultsafe del my_mnemonic
```

### Open Credential

#### `open`
Retrieve and display a credential from the database. If the credential's URL entry is not None, open the URL in a web browser.

**Argument:**
- -mnemonic (str): Mnemonic of the credential to be opened.

**Example**:
```sh
vaultsafe open my_mnemonic
```

### Change Master Password

#### `change-master-password`
Change the master password for the password vault.

**Example**:
```sh
vaultsafe change-master-password
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
vaultsafe update-vault -n "New Vault Name" -o "New Owner Name"
vaultsafe update-vault -e "newemail@example.com"
```

### Import/Export

#### `export`
Export credentials to a specified file format.

Options:
- -o, --output_dir (str): Directory where the exported file will be saved.
- -f, --file_format (str): File format for export ('json' or 'csv'). Defaults to 'json'.

**Example**:
```sh
vaultsafe export --output-dir /path/to/export --file-format csv
```

#### `import`
Import credentials from a JSON or CSV file into the database.

**Arg:**
- file_path (str): Path to the file containing credentials data.

**Option:**
- -f, --format (str): File format ('json' or 'csv').

**Example**:
```sh
vaultsafe import /path/to/credentials.csv --format csv
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
