# This script handles the add command.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import click
import pwinput
from password_manager.db.models import session, Credential, Mnemonic, Vault
from password_manager.utils.cli_utils import input_password
from password_manager.utils.auth_utils import get_password
from password_manager.utils.crypto_utils import derive_vault_key, encrypt, generate_fernet_key


@click.command()
@click.option('-n', '--name', required=True, help='Name for the credential')
@click.option('-mn', '--mnemonics', required=True, multiple=True, help='Mnemonics for the credential')
@click.option('-u', '--username', required=False, help='Username for the credential')
@click.option('-p', '--password', required=False, help='Password for the credential')
@click.option('-url', '--url', required=False, help='URL for the credential')
def add(name, mnemonics, username, password, url):
    """Add a new credential."""
    master_passwd = input_password(info_msg="Enter your app password: ")

    vault = session.query(Vault).first()
    if not vault:
        click.echo("Vault not initialized.")
        return
    
    # Check master_password
    if not vault.check_password(master_passwd):
        click.echo("Sorry wrong password!")
        return
    
    # Take credential details
    if name is None:
        name = input("Enter a name for the credential (e.g- 'My Facebook account' or 'Gmail 2014 Account'): ")
    if url is None:
        url = input("Enter the url of the credential (optional): ")
    if username is None:
        username = input("Enter the username for the credential (optional): ")
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

    # Add the credential to the db
    session.add(credential)
    
    # Add mnemonics
    
    # Query all mnemonics
    existing_mnemonics = session.query(Mnemonic).all()

    # Set the mnemonics to the Credential
    for mnemonic in mnemonics:
        if not mnemonic in existing_mnemonics:
            mnemonic_entry = Mnemonic(name=mnemonic, credential=credential)
            session.add(mnemonic_entry)
        else:
            print(f" - NOTE: the mnemonic '{mnemonic}' already exists in the database and cannot be used for a new credential. Skipped!")

    session.commit()

    click.echo(f"Credential '{credential.name}' added.")
