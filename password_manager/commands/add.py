# This script handles the add command.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import click
from password_manager.db.models import session, Credential, Mnemonic, Vault
from password_manager.utils.cli_utils import input_password
from password_manager.utils.auth_utils import get_password, input_master_passwd_and_verify
from password_manager.utils.crypto_utils import derive_vault_key, encrypt, generate_fernet_key


@click.command()
@click.option('-n', '--name', required=True, help='Name for the credential')
@click.option('-mn', '--mnemonics', required=True, multiple=True, help='Mnemonics for the credential')
@click.option('-u', '--username', required=False, help='Username for the credential')
@click.option('-p', '--password', required=False, help='Password for the credential')
@click.option('-url', '--url', required=False, help='URL for the credential')
def add(name, mnemonics, username, password, url):
    """Add a new credential."""
    master_passwd = input_master_passwd_and_verify()
    
    # Take credential details
    if name is None:
        name = click.prompt("Enter a name for the credential (e.g- 'My Facebook account' or 'Gmail 2014 Account')")
    if url is None:
        url = click.prompt("Enter the url of the credential (optional)", default='')
    if username is None:
        username = click.prompt("Enter the username for the credential (optional)", default='')
    if password is None:
        password = get_password(info_msg="Enter the password for the credential (optional): ", success_msg='')

    
    # Derive the vault_key
    vault_key = derive_vault_key(master_key=master_passwd)

    # New key for the credential
    credential_key = generate_fernet_key()

    encrypted_username = encrypt(username, credential_key) if username else None
    encrypted_password = encrypt(password, credential_key) if password else None
    encrypted_url = encrypt(url, credential_key) if url else None
    encrypted_credential_key = encrypt(credential_key, vault_key)

    # Create the credential
    credential = Credential(
        name = name,
        url = encrypted_url,
        username = encrypted_username,
        password = encrypted_password,
        encrypted_key = encrypted_credential_key
    )

    # Query all mnemonics
    existing_mnemonics = session.query(Mnemonic.name).all()
    existing_mnemonic_names = {mnemonic.name for mnemonic in existing_mnemonics}

    # Check if any of the provided mnemonics already exist
    for mnemonic in mnemonics:
        if mnemonic in existing_mnemonic_names:
            click.echo(f" - NOTE: the mnemonic '{mnemonic}' already exists in the database and cannot be used for a new credential. Skipped!")
            return

    # Add the credential to the db
    session.add(credential)
    session.commit()

    # Set the mnemonics to the Credential
    for mnemonic in mnemonics:
        mnemonic_entry = Mnemonic(name=mnemonic, credential=credential)
        session.add(mnemonic_entry)

    session.commit()

    click.echo(f"Credential with the name '{credential.name}' added.")
