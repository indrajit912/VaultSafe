# This script handles the init command.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import click
import shutil
import pprint

from password_manager.db.models import Base, engine, session, Vault
from password_manager.utils.auth_utils import get_password
from password_manager.utils.crypto_utils import derive_vault_key
from password_manager.utils.cli_utils import clear_terminal_screen
from config import DATABASE_PATH, DOT_PASSWD_MANGR_DIR


def init_db(clear_screen:bool=True):
    if clear_screen:
        clear_terminal_screen()

    if not DATABASE_PATH.exists():
        
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(engine)

        # Take the `master_password` from user
        master_passwd = get_password(
            info_msg="[-] Enter a password for the app (e.g. your system passwd): ", 
            success_msg="- Master password set successfully. Please remember this password for future use!"
        )

        # Prompt user for optional attributes
        vault_name = input("[-] Enter a name for the vault (optional, defaults to system's hostname): ")
        owner_name = input("[-] Enter your name (optional, defaults to system's current user): ")
        owner_email = input("[-] Enter your email (optional, defaults to None): ")

        # Create a Vault instance
        vault = Vault(
            name=None if vault_name == '' else vault_name,
            owner_name=None if owner_name == '' else owner_name,
            owner_email=None if owner_email == '' else owner_email
        )

        # Set the sha256 hash value of `master_key`
        vault.set_master_password_hash(master_password=master_passwd)

        # Derive `vault_key` from the `master_key`
        vault_key = derive_vault_key(master_key=master_passwd)

        # Set the sha256 has value of `vault_key`
        vault.set_vault_key_hash(vault_key=vault_key)

        # Add the vault instance to the session and commit it to the database
        session.add(vault)
        session.commit()

        print("\n[-] Password Vault initialized.\n")

        # Print the hashes to verify
        pprint.pprint(vault.json())
    else:
        print("Vault already exists.")
        res = input("[-] Do you want to delete all existing data and start afresh? (y/n): ")
        if res.lower() == 'y':
            shutil.rmtree(DOT_PASSWD_MANGR_DIR)
            print("Existing vault deleted.")
            init_db(clear_screen=False)  # Call init_db again to recreate the database

@click.command()
def init():
    """Initialize the database."""
    init_db()