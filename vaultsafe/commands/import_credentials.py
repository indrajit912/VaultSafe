# This script handles the import command.
# Author: Indrajit Ghosh
# Created On: Jun 14, 2024
# 
import json

import click
from sqlalchemy.exc import IntegrityError
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from vaultsafe.db.models import session, Credential, Mnemonic
from vaultsafe.utils.crypto_utils import encrypt, decrypt, generate_fernet_key, derive_vault_key, sha256_hash
from vaultsafe.utils.auth_utils import input_master_passwd_and_verify
from vaultsafe.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

def _decrypt_attr(attr, key):
    return decrypt(attr, key) if attr else None


def import_credentials_from_json(file_path, vault_key):
    """
    Import credentials from a JSON file into the database.

    Parameters:
    - file_path (str): Path to the JSON file containing credentials data.
    - vault_key (bytes): Vault key to encrypt the key of each Credentials.
    """
    with open(file_path, 'r') as f:
        filedata = json.load(f)

    metadata = filedata.get('metadata')
    if metadata is None:
        err_message = "[red]Error:[/red] The file structure is unknown. Cannot be imported."
        rprint('\n', Panel(err_message, title="Import Error", title_align="left", highlight=True, padding=1), '\n')
        return

    credentials_data = filedata.get('credentials', [])

    file_encrypted = metadata.get('file_encrypted')
    
    if file_encrypted:
        # Ask the user for the file password.
        file_passwd = click.prompt("Enter the file password")

        # Derive the file key
        file_key = derive_vault_key(master_key=file_passwd)

        # Match the file key hash
        file_key_hash = metadata.get('file_key_hash')
        if not file_key_hash == sha256_hash(file_key):
            err_message = "[red]Error:[/red] The password you entered is incorrect. Please try again."
            rprint('\n', Panel(err_message, title="Password Error", title_align="left", highlight=True, padding=1), '\n')
            return


    for data in credentials_data:
        name = data.get('name')

        if file_encrypted:
            # Get the old encrypted_key
            old_credential_key_encrypted = data.get('encrypted_key').encode()

            # Decrypt the key
            old_credential_key = decrypt(old_credential_key_encrypted, file_key)

        url = _decrypt_attr(data.get('url'), old_credential_key) if file_encrypted else data.get('url')
        username = _decrypt_attr(data.get('username'), old_credential_key) if file_encrypted else data.get('username')
        password = _decrypt_attr(data.get('password'), old_credential_key) if file_encrypted else data.get('password')
        recovery_key = _decrypt_attr(data.get('recovery_key'), old_credential_key) if file_encrypted else data.get('recovery_key')
        primary_email = _decrypt_attr(data.get('primary_email'), old_credential_key) if file_encrypted else data.get('primary_email')
        secondary_email = _decrypt_attr(data.get('secondary_email'), old_credential_key) if file_encrypted else data.get('secondary_email')
        token = _decrypt_attr(data.get('token'), old_credential_key) if file_encrypted else data.get('token')
        notes = _decrypt_attr(data.get('notes'), old_credential_key) if file_encrypted else data.get('notes')

        mnemonics = list(set([m.strip() for m in data.get('mnemonics', '').split(',') if m.strip()]))

        try:
            # Check if any mnemonic is already associated with an existing credential
            existing_mnemonics = session.query(Mnemonic).filter(Mnemonic.name.in_(mnemonics)).all()

            if existing_mnemonics:
                console.print(f"Skipping credential '{name}' due to existing mnemonic association.")
                continue

            # Create Credential object
            # Generate a new key for the credential
            credential_key = generate_fernet_key()

            # Encrypt credentials
            encrypted_username = encrypt(username, credential_key) if username else None
            encrypted_password = encrypt(password, credential_key) if password else None
            encrypted_url = encrypt(url, credential_key) if url else None
            recovery_key_encrypted = encrypt(recovery_key, credential_key) if recovery_key else None
            primary_email_encrypted = encrypt(primary_email, credential_key) if primary_email else None
            secondary_email_encrypted = encrypt(secondary_email, credential_key) if secondary_email else None
            token_encrypted = encrypt(token, credential_key) if token else None
            notes_encrypted = encrypt(notes, credential_key) if notes else None
            encrypted_credential_key = encrypt(credential_key, vault_key)

            # Create the credential object
            credential = Credential(
                name=name,
                url=encrypted_url,
                username=encrypted_username,
                password=encrypted_password,
                encrypted_key=encrypted_credential_key,
                recovery_key=recovery_key_encrypted,
                primary_email=primary_email_encrypted,
                secondary_email=secondary_email_encrypted,
                token=token_encrypted,
                notes=notes_encrypted
            )

            # Add the credential to the database
            session.add(credential)
            session.commit()

            # Associate mnemonics with the credential
            for mnemonic in mnemonics:
                mnemonic_entry = Mnemonic(name=mnemonic, credential=credential)
                session.add(mnemonic_entry)
            
            session.commit()

            console.print(f"Imported credential '{name}' successfully.")

        except IntegrityError as e:
            session.rollback()
            console.print(f"[bold red]Error:[/bold red] Failed to import credential '{name}'. {str(e)}")


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['json']), default='json',
              help='File format for import (json).')
def import_credentials(file_path, format):
    """
    Import credentials from a JSON file into the database.

    This command imports credentials into the database. Mnemonics are checked to avoid duplication.

    Arg:
    - file_path (str): Path to the file containing credentials data.

    Option:
    -f, --format (str): File format ('json').

    Example usage:
    \b
    $ vaultsafe import /path/to/credentials.csv --format csv
    """
    print_basic_info()
    assert_db_init()

    console.rule("Import Credentials")

    # Take master password
    master_passwd = input_master_passwd_and_verify()
    
    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    if format == 'json':
        import_credentials_from_json(file_path, vault_key)
    elif format == 'txt':
        # TODO: Let the user that txt file cannot be imported.
        pass

