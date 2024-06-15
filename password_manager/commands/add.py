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
@click.option('-u', '--username', is_flag=True, help='Username for the credential')
@click.option('-p', '--password', is_flag=True, help="Flag to add the password.")
@click.option('-k', '--recovery-key', is_flag=True, help='Recovery key (if any) for the credential')
@click.option('-url', '--url', is_flag=True, help='URL for the credential')
@click.option('-pe', '--primary-email', is_flag=True, help='Primary email id associated with the credential')
@click.option('-se', '--secondary-email', is_flag=True, help='Secondary email id associated with the credential')
@click.option('-t', '--token', is_flag=True, help="Flag to add any token for the credential.")
@click.option('-nt', '--notes', is_flag=True, help='Notes that could be stored along with the credential')
def add(name, mnemonics, username, password, recovery_key, url, primary_email, secondary_email, token, notes):
    """
    Add a new credential to the database.

    This command adds a new credential to the password vault database. It allows specifying 
    various attributes of the credential, including name, mnemonics, username, password, 
    recovery key, URL, primary email, secondary email, token, and notes.

    Options:
        -n, --name TEXT: Name for the credential (required).
        -mn, --mnemonics TEXT: Mnemonics associated with the credential (required, multiple values).
        -u, --username: Flag to add the username for the credential.
        -p, --password: Flag to add the password for the credential.
        -k, --recovery-key: Flag to add the recovery key (if any) for the credential.
        -url, --url: Flag to add the URL for the credential.
        -pe, --primary-email: Flag to add the primary email id associated with the credential.
        -se, --secondary-email: Flag to add the secondary email id associated with the credential.
        -t, --token: Flag to add any token for the credential.
        -nt, --notes: Flag to add notes that could be stored along with the credential.

    Examples:
        To add a credential with a name and mnemonics:
        \b
        $ password-manager add -n "My Credential Name" -mn mnemonic1 -mn mnemonic2

        To add a credential with all details (name, mnemonics, username, password, and URL):
        \b
        $ password-manager add -n "My Facebook Account" -mn fb -mn facebook -u -p -url

        To add a credential with additional details (recovery key, primary email, secondary email, token, and notes):
        \b
        $ password-manager add -n "My Credential" -mn mnemonic1 -mn mnemonic2 -u -p -k -url -pe -se -t -nt
    """
    print_basic_info()
    assert_db_init()

    console.rule("Add Credential")

    # Take master password
    master_passwd = input_master_passwd_and_verify()

    # Prompt for credential details if not provided as options
    if username:
        username = click.prompt("Enter the username for the credential", default='')
    # Add password if flag is provided
    if password:
        password = get_password(
            info_msg="Give the password for the credential: ",
            success_msg="Passwords matched!"
        )
        console.print(Panel("[bold green]Credential's password added successfully![/bold green]", style="bold green"))

    if url:
        url = click.prompt("Enter the URL for the credential", default='')
    if primary_email:
        primary_email = click.prompt("Enter the primary email id associated with the credential", default='')
    if secondary_email:
        secondary_email = click.prompt("Enter the secondary email id associated with the credential", default='')
    if token:
        token = click.prompt("Enter the token (if any) associated with this credential", default='')
    if notes:
        notes = click.prompt("Write any notes related to the credential", default='')
    
    # Add token if flag is provided
    if token:
        token = get_password(
            info_msg="Enter the token: ",
            success_msg="Tokens matched!"
        )
        console.print(Panel("[bold green]Credential's token added successfully![/bold green]", style="bold green"))

    # Add recovery key if flag is provided
    if recovery_key:
        recovery_key = get_password(
            info_msg="Enter the recovery key: ",
            success_msg="Recovery keys matched!"
        )
        console.print(Panel("[bold green]Credential's recovery key added successfully![/bold green]", style="bold green"))

    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    # Generate a new key for the credential
    credential_key = generate_fernet_key()

    # Encrypt credentials
    encrypted_username = encrypt(username, credential_key) if username else None
    encrypted_password = encrypt(password, credential_key) if password else None
    encrypted_url = encrypt(url, credential_key) if url else None
    encrypted_recovery_key = encrypt(recovery_key, credential_key) if recovery_key else None
    encrypted_primary_email = encrypt(primary_email, credential_key) if primary_email else None
    encrypted_secondary_email = encrypt(secondary_email, credential_key) if secondary_email else None
    encrypted_token = encrypt(token, credential_key) if token else None
    encrypted_notes = encrypt(notes, credential_key) if notes else None

    encrypted_credential_key = encrypt(credential_key, vault_key)

    # Create the credential object
    credential = Credential(
        name=name,
        url=encrypted_url,
        username=encrypted_username,
        password=encrypted_password,
        encrypted_key=encrypted_credential_key,
        token=encrypted_token,
        recovery_key=encrypted_recovery_key,
        primary_email=encrypted_primary_email,
        secondary_email=encrypted_secondary_email,
        notes=encrypted_notes
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
