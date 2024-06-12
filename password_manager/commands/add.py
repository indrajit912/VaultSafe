# This script handles the add command.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import click
from password_manager.db.models import Session, Credential

@click.command()
@click.option('-url', '--url', required=True, help='URL for the credential')
@click.option('-m', '--mnemonic', required=True, multiple=True, help='Mnemonics for the credential')
@click.option('-u', '--username', required=False, help='Username for the credential')
@click.option('-p', '--password', required=False, help='Password for the credential')
def add(mnemonic, username, password, url):
    """Add a new credential."""
    app_passwd = click.prompt('Enter your application password', hide_input=True)
    print(app_passwd)

    print(mnemonic)
    print(url)
    print(username)
    print(password)

    click.echo(f"Credential '{mnemonic}' added.")
