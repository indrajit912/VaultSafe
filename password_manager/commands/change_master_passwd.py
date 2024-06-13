# This script is used to change the `master_password`.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import click
import pwinput
from rich.console import Console
from rich.panel import Panel

from password_manager.db.models import session, Vault, Credential
from password_manager.utils.auth_utils import input_master_passwd_and_verify
from password_manager.utils.crypto_utils import derive_vault_key, encrypt, decrypt
from password_manager.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
def change_master_password():
    """
    Command to change the master password for the password vault.

    This command allows the user to change the master password used to encrypt and decrypt
    credentials stored in the password vault.

    Notes:
        - This command requires the database to be initialized (`init` command).
        - User input for passwords is masked for security.
        - If the entered new passwords do not match, the operation is aborted.

    Example:
        To change the master password:
        
        $ password-manager change-master-password
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("[bold cyan]Change Master Password[/bold cyan]")
    
    # Take old master password
    old_master_passwd = input_master_passwd_and_verify()

    # Derive the old vault key
    old_vault_key = derive_vault_key(master_key=old_master_passwd)

    # Prompt for new master password
    console.print("[bold]Enter new master password: [/bold]", style="bold cyan", end='')
    new_master_passwd = pwinput.pwinput("", mask='\u2022')

    # Prompt to confirm new master password
    console.print("[bold]Confirm new master password: [/bold]", style="bold cyan", end='')
    confirm_new_master_passwd = pwinput.pwinput("", mask='\u2022')

    if new_master_passwd != confirm_new_master_passwd:
        console.print("[bold red]Passwords do not match. Aborting operation.[/bold red]")
        return

    # Derive the new vault key
    new_vault_key = derive_vault_key(master_key=new_master_passwd)

    # Get the vault
    vault = session.query(Vault).first()

    # Set new password hashes
    vault.set_master_password_hash(new_master_passwd)
    vault.set_vault_key_hash(new_vault_key)

    # Update credentials with new vault key
    credentials = session.query(Credential).all()
    for cred in credentials:
        cred_key = decrypt(cred.encrypted_key, old_vault_key)
        cred_key_encrypted = encrypt(cred_key, new_vault_key)
        cred.encrypted_key = cred_key_encrypted

    session.commit()

    console.print(Panel("[bold green]Master password changed successfully![/bold green]", style="bold green"))
