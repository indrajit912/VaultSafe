# This script handles the add command.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import click
from rich.console import Console
from rich.panel import Panel

from password_manager.db.models import session, Credential, Mnemonic
from password_manager.utils.auth_utils import get_password, input_master_passwd_and_verify
from password_manager.utils.crypto_utils import derive_vault_key, encrypt, generate_fernet_key
from password_manager.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.option('-n', '--name', required=True, help='Name for the credential')
@click.option('-mn', '--mnemonics', required=True, multiple=True, help='Mnemonics for the credential')
@click.option('-u', '--username', required=False, help='Username for the credential')
@click.option('-p', '--password', required=False, help='Password for the credential')
@click.option('-url', '--url', required=False, help='URL for the credential')
def add(name, mnemonics, username, password, url):
    """
    Add a new credential to the database.

    Args:
        name (str): Name for the credential (required).
        mnemonics (list): Mnemonics associated with the credential (required, multiple values).
        username (str, optional): Username for the credential.
        password (str, optional): Password for the credential.
        url (str, optional): URL associated with the credential.

    Notes:
        - This command requires the database to be initialized ('init' command).
        - Mnemonics provided must be unique and not already associated with other credentials.

    Examples:
        To add a credential with a name and mnemonics:
        \b
        $ password-manager add -n MyCredential -mn mnemonic1 mnemonic2

        To add a credential with all details (name, mnemonics, username, password, and URL):
        \b
        $ password-manager add -n MyCredential -mn mnemonic1 mnemonic2 -u username -p password -url https://example.com

    """
    print_basic_info()
    assert_db_init()

    console.rule("Add Credential")

    # Take master password
    master_passwd = input_master_passwd_and_verify()

    # Prompt for credential details if not provided as options
    if username is None:
        username = click.prompt("Enter the username for the credential (optional)", default='')
    if password is None:
        password = get_password(info_msg="Enter the password for the credential (optional): ", success_msg='Password saved.')
    if url is None:
        url = click.prompt("Enter the URL for the credential (optional)", default='')

    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    # Generate a new key for the credential
    credential_key = generate_fernet_key()

    # Encrypt credentials
    encrypted_username = encrypt(username, credential_key) if username else None
    encrypted_password = encrypt(password, credential_key) if password else None
    encrypted_url = encrypt(url, credential_key) if url else None
    encrypted_credential_key = encrypt(credential_key, vault_key)

    # Create the credential object
    credential = Credential(
        name=name,
        url=encrypted_url,
        username=encrypted_username,
        password=encrypted_password,
        encrypted_key=encrypted_credential_key
    )

    # Check if any of the provided mnemonics already exist
    existing_mnemonics = session.query(Mnemonic.name).filter(Mnemonic.name.in_(mnemonics)).all()
    existing_mnemonic_names = {mnemonic.name for mnemonic in existing_mnemonics}

    for mnemonic in mnemonics:
        if mnemonic in existing_mnemonic_names:
            console.print(f"[yellow]Note: The mnemonic '{mnemonic}' already exists and cannot be reused for a new credential. Skipped![/yellow]")
            return

    # Add the credential to the database
    session.add(credential)
    session.commit()

    # Associate mnemonics with the credential
    for mnemonic in mnemonics:
        mnemonic_entry = Mnemonic(name=mnemonic, credential=credential)
        session.add(mnemonic_entry)

    session.commit()

    console.print(Panel(f"Credential '{credential.name}' added successfully!", title="Success", style="bold green"))

    # Print the credential
    credential.print_on_screen(vault_key=vault_key, copy_to_clipboard=False)
