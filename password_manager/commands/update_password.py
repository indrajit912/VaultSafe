# ------------------ NOTE: This script is no longer needed!------------
# This script is used to update the `password` of an existing credential.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import click
from rich.console import Console
from rich.panel import Panel

from password_manager.db.models import session, Credential, Mnemonic
from password_manager.utils.auth_utils import input_master_passwd_and_verify, get_password
from password_manager.utils.crypto_utils import derive_vault_key, encrypt
from password_manager.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.argument('mnemonic', required=True)
@click.option('--password', is_flag=True, help="Flag to update the password.")
@click.option('--token', is_flag=True, help="Flag to update the token.")
@click.option('--recovery-key', is_flag=True, help="Flag to update the recovery key.")
def update_password(mnemonic, password, token, recovery_key):
    """
    Command to update the attributes of an existing credential.

    This command updates the password, token, and/or recovery key of a credential stored in the password vault.
    The credential is identified by a mnemonic provided as an argument. The user is prompted to enter the new 
    values for the specified attributes, which are then encrypted and stored in the database.

    Args:
        mnemonic (str): The mnemonic identifier of the credential whose attributes are to be updated.
        password (bool): Flag to update the password.
        token (bool): Flag to update the token.
        recovery_key (bool): Flag to update the recovery key.

    Example:
        To update the password of a credential identified by the mnemonic 'my_mnemonic':
        \b
        $ password-manager update-credential my_mnemonic --password
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("[bold cyan]Update Credential[/bold cyan]")

    # Get the credential
    credential = session.query(Credential).join(Mnemonic).filter(Mnemonic.name == mnemonic).first()

    if not credential:
        console.print(f"[yellow]Credential not found with the provided identifier '{mnemonic}'. Update operation aborted.[/yellow]")
        return
    
    # Take old master password
    master_passwd = input_master_passwd_and_verify()

    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    # Get the cred_key
    cred_key = credential.get_decrypted_key(vault_key=vault_key)

    # Update password if flag is provided
    if password:
        new_password = get_password(
            info_msg="Give the new password for the credential: ",
            success_msg="Passwords matched!"
        )
        new_password_encrypted = encrypt(new_password, cred_key)
        credential.password = new_password_encrypted
        console.print(Panel("[bold green]Credential's password changed successfully![/bold green]", style="bold green"))
    
    # Update token if flag is provided
    if token:
        new_token = click.prompt("Enter the new token", hide_input=True, confirmation_prompt=True)
        new_token_encrypted = encrypt(new_token, cred_key)
        credential.token = new_token_encrypted
        console.print(Panel("[bold green]Credential's token changed successfully![/bold green]", style="bold green"))

    # Update recovery key if flag is provided
    if recovery_key:
        new_recovery_key = click.prompt("Enter the new recovery key", hide_input=True, confirmation_prompt=True)
        new_recovery_key_encrypted = encrypt(new_recovery_key, cred_key)
        credential.recovery_key = new_recovery_key_encrypted
        console.print(Panel("[bold green]Credential's recovery key changed successfully![/bold green]", style="bold green"))

    # Commit the changes
    session.commit()