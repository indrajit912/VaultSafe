# This script handles the init command.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import click
import shutil
import socket
import getpass

from password_manager.db.models import Base, engine, session, Vault
from password_manager.utils.auth_utils import get_password
from password_manager.utils.crypto_utils import derive_vault_key
from config import DATABASE_PATH, DOT_PASSWD_MANGR_DIR

@click.command()
def init():
    """Initialize the database."""
    init_db()

def init_db():

    if not DATABASE_PATH.exists():
        # Create database and tables if they don't exist
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(engine)

        click.secho("\nPassword Vault Initialization", fg="cyan", bold=True)
        click.echo()

        # Take the `master_password` from user
        click.echo("[*] Setting up your password vault...")
        master_passwd = get_password(
            info_msg="[-] Enter a password for the app (e.g. your system password): ",
            success_msg="Master password set successfully. Please remember this password for future use!"
        )

        # Prompt user for optional attributes
        vault_name = click.prompt("[-] Enter a name for the vault", default=socket.gethostname())
        owner_name = click.prompt("[-] Enter your name", default=getpass.getuser())
        owner_email = click.prompt("[-] Enter your email (optional)", default='')

        # Create a Vault instance
        vault = Vault(
            name=vault_name if vault_name else None,
            owner_name=owner_name if owner_name else None,
            owner_email=owner_email if owner_email else None
        )

        # Set the sha256 hash value of `master_key`
        vault.set_master_password_hash(master_password=master_passwd)

        # Derive `vault_key` from the `master_key`
        vault_key = derive_vault_key(master_key=master_passwd)

        # Set the sha256 hash value of `vault_key`
        vault.set_vault_key_hash(vault_key=vault_key)

        # Add the vault instance to the session and commit it to the database
        session.add(vault)
        session.commit()

        click.echo("\n[-] Password Vault initialized successfully.\n")

        # Print the vault information
        vault.print_on_screen()

    else:
        click.secho("Vault already exists.", fg="yellow")
        res = click.prompt("[-] Do you want to delete all existing data and start afresh? (y/n)")
        if res.lower() == 'y':
            shutil.rmtree(DOT_PASSWD_MANGR_DIR)
            click.echo("Existing vault deleted.")
            init_db()  # Recreate the database after deletion


