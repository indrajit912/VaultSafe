# /utils/auth_utils.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
#
import pwinput
import sys
import click
from rich.console import Console
from rich.panel import Panel

from password_manager.utils.cli_utils import input_password
from password_manager.db.models import session, Vault

console = Console()

def get_password(info_msg: str = "Enter your password: ", success_msg: str = "Password set successfully!"):
    """
    Prompt user to enter a password securely and confirm it.

    Parameters:
    info_msg (str): Message to display when prompting for password.
    success_msg (str): Message to display upon successful password entry.

    Returns:
    str: The entered password.
    """
    bullet_unicode = '\u2022'
    while True:
        password1 = pwinput.pwinput(info_msg, mask=bullet_unicode)
        if password1 == '':
            return ''
        password2 = pwinput.pwinput("Confirm your password: ", mask=bullet_unicode)
        if password1 == password2:
            console.print(Panel(f"[bold green]{success_msg}[/bold green]", border_style="green"))
            return password1
        else:
            click.echo("Passwords do not match. Please try again.")

def input_master_passwd_and_verify():
    """
    Take the master_passwd from user and verify it. If everything
    is ok then returns the user input.
    """
    bullet_unicode = '\u2022'
    master_passwd = pwinput.pwinput("Enter your app password: ", mask=bullet_unicode)

    vault = session.query(Vault).first()
    if not vault:
        console.print(Panel("[bold red]Vault not initialized. First use 'init' command to initialize a new Vault.[/bold red]", border_style="red"))
        sys.exit(1)
    
    # Check master_password
    if not vault.check_password(master_passwd):
        console.print(Panel("[bold red]Sorry, wrong password![/bold red]", border_style="red"))
        sys.exit(1)
    
    console.print(Panel("[bold green]Password verified successfully![/bold green]", border_style="green"))
    return master_passwd