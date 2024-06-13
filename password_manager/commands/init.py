# This script handles the init command.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import click
import shutil
import socket
import getpass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from password_manager.db.models import Base, engine, session, Vault
from password_manager.utils.auth_utils import get_password
from password_manager.utils.crypto_utils import derive_vault_key
from password_manager.utils.cli_utils import print_basic_info
from password_manager.config import DATABASE_PATH, DOT_PASSWD_MANGR_DIR

console = Console()

@click.command()
def init():
    """
    Initialize the password vault.

    This command sets up the password vault database if it doesn't already exist. If the database exists,
    it provides an option to delete all existing data and start fresh.

    Notes:
        - The command initializes the database where credentials and vault information are stored.
        - It prompts for the master password and optional vault attributes like name, owner name, and owner email.
        - If the database already exists, it prompts to confirm deleting all existing data before reinitializing.

    Example:
        To initialize the password vault:
        \b
        $ password-manager init

    """
    print_basic_info()
    init_db()

def init_db():
    if not DATABASE_PATH.exists():
        # Create database and tables if they don't exist
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(engine)

        console.rule("[bold cyan]Password Vault Initialization[/bold cyan]")
        console.print("\n")

        # Take the `master_password` from user
        console.print("[*] Setting up your password vault...")
        master_passwd = get_password(
            info_msg="Enter a password for the app (e.g. your system password): ",
            success_msg="Master password set successfully. Please remember this password for future use!"
        )

        # Prompt user for optional attributes
        vault_name = Prompt.ask("[bold yellow][-] Enter a name for the vault", default=socket.gethostname())
        owner_name = Prompt.ask("[bold yellow][-] Enter your name", default=getpass.getuser())
        owner_email = Prompt.ask("[bold yellow][-] Enter your email (optional)", default='')

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
        console.print(Panel("[bold green]Password Vault initialized successfully.[/bold green]", border_style="green"))

        # Print the vault information
        vault.print_on_screen()

    else:
        console.print(Panel("[bold yellow]Vault already exists.[/bold yellow]", border_style="yellow"))
        res = Prompt.ask("[-] Do you want to delete all existing data and start afresh? (y/n)")
        if res.lower() == 'y':
            shutil.rmtree(DOT_PASSWD_MANGR_DIR)
            console.print(Panel("[bold red]Existing vault deleted.[/bold red]", border_style="red"))
            init_db()  # Recreate the database after deletion

