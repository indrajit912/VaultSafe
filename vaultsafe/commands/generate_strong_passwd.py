# This script handles the generate command.
# Author: Indrajit Ghosh
# Created On: Jun 15, 2024
#
import click
import secrets
import string

import pyperclip
from rich.console import Console
from rich.table import Table

from vaultsafe.utils.cli_utils import print_basic_info, assert_db_init

console = Console()

def generate_strong_password(length=15):
    """
    Generate a strong password of specified length.
    
    Args:
        length (int): Length of the password to be generated.
        
    Returns:
        str: The generated strong password.
    """
    if length < 4:
        raise ValueError("Password length must be at least 4 characters.")
    
    characters = string.ascii_letters + string.digits + "@#$-%&"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

@click.command()
@click.option('-l', '--length', default=18, help='Length of the generated password.')
@click.option('-c', '--count', default=1, help='Number of passwords to generate.')
def generate(length, count):
    """
    Generate strong passwords of specified length.

    Options:
        -l, --length (int): Length of the password to be generated. Default is 16.
        -c, --count (int): Number of passwords to generate. Default is 1.

    Examples:
        To generate a single password of default length (16 characters):
        \b
        $ vaultsafe generate

        To generate a single password of specified length:
        \b
        $ vaultsafe generate --length 20

        To generate multiple passwords of specified length:
        \b
        $ vaultsafe generate --length 20 --count 3

    """
    print_basic_info()
    assert_db_init()
    
    console.rule("Generate Strong Passwords")
    
    try:
        passwords = [generate_strong_password(length) for _ in range(count)]
        
        table = Table(title="Generated Passwords")
        table.add_column("Index", justify="right", style="cyan", no_wrap=True)
        table.add_column("Password", style="magenta")
            
        for i, password in enumerate(passwords, start=1):
            table.add_row(str(i), password)
            
        console.print(table)

        if len(passwords) == 1:
            pyperclip.copy(passwords[0])
            console.print("[bold yellow]Password has been copied to clipboard.[/bold yellow]")
            
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

