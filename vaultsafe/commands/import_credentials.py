# This script handles the import command.
# Author: Indrajit Ghosh
# Created On: Jun 14, 2024
# 
import json
import csv

import click
from sqlalchemy.exc import IntegrityError
from rich.console import Console

from vaultsafe.db.models import session, Credential, Mnemonic
from vaultsafe.utils.crypto_utils import encrypt, generate_fernet_key
from vaultsafe.utils.auth_utils import input_master_passwd_and_verify
from vaultsafe.utils.crypto_utils import derive_vault_key
from vaultsafe.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

def import_credentials_from_json(file_path, vault_key):
    """
    Import credentials from a JSON file into the database.

    Parameters:
    - file_path (str): Path to the JSON file containing credentials data.
    - vault_key (bytes): Vault key to encrypt the key of each Credentials.
    """
    with open(file_path, 'r') as f:
        credentials_data = json.load(f)

    for data in credentials_data:
        name = data.get('name')
        url = data.get('url')
        username = data.get('username')
        password = data.get('password')
        recovery_key = data.get('recovery_key')
        primary_email = data.get('primary_email')
        secondary_email = data.get('secondary_email')
        token = data.get('token')
        notes = data.get('notes')
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

def import_credentials_from_csv(file_path, vault_key):
    """
    Import credentials from a CSV file into the database.

    Parameters:
    - file_path (str): Path to the CSV file containing credentials data.
    - vault_key (bytes): Vault key to encrypt the key of each Credentials.
    """
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row.get('name')
            url = row.get('url')
            username = row.get('username')
            password = row.get('password')
            recovery_key = row.get('recovery_key')
            primary_email = row.get('primary_email')
            secondary_email = row.get('secondary_email')
            token = row.get('token')
            notes = row.get('notes')
            mnemonics = list(set([m.strip() for m in row.get('mnemonics', '').split(',') if m.strip()]))

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
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), required=True,
              help='File format for import (json or csv).')
def import_credentials(file_path, format):
    """
    Import credentials from a JSON or CSV file into the database.

    This command imports credentials into the database. Mnemonics are checked to avoid duplication.

    Arg:
    - file_path (str): Path to the file containing credentials data.

    Option:
    -f, --format (str): File format ('json' or 'csv').

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
    elif format == 'csv':
        import_credentials_from_csv(file_path, vault_key)

