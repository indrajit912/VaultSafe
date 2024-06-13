# This script handles the update command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
# 
import click
from rich.console import Console
from rich.panel import Panel

from password_manager.db.models import session, Credential, Mnemonic
from password_manager.utils.auth_utils import input_master_passwd_and_verify
from password_manager.utils.crypto_utils import derive_vault_key, encrypt

console = Console()
# TODO: Add code to update mnemonics
@click.command()
@click.argument('mnemonic', required=False)
@click.option('--uuid', help='UUID associated with the credential to update')
@click.option('-n', '--name', help='Updated name for the credential')
@click.option('-mn', '--mnemonics', required=True, multiple=True, help='Mnemonics for the credential')
@click.option('-u', '--username', help='Updated username for the credential')
@click.option('-p', '--password', help='Updated password for the credential')
@click.option('-url', '--url', help='Updated URL for the credential')
def update(mnemonic, uuid, name, mnemonics, username, password, url):
    """
    Update an existing credential.
    """
    console.rule("Update Credential")

    # Ensure at least one of mnemonic or uuid is provided
    if not (mnemonic or uuid):
        console.print("[yellow]Please provide either 'mnemonic' or 'uuid' to identify the credential to update.[/yellow]")
        return

    # Take master password
    master_passwd = input_master_passwd_and_verify()

    # Query credential based on mnemonic or uuid
    if mnemonic:
        credential = session.query(Credential).join(Mnemonic).filter(Mnemonic.name == mnemonic).first()
    elif uuid:
        credential = session.query(Credential).filter_by(uuid=uuid).first()

    if not credential:
        console.print(f"[yellow]Credential not found with the provided mnemonic '{mnemonic or uuid}'. Update operation aborted.[/yellow]")
        return

    # Derive vault key
    vault_key = derive_vault_key(master_key=master_passwd)
    credential_key = credential.get_decrypted_key(vault_key=vault_key)

    # Update credential fields if provided
    if name:
        credential.name = name
    if username:
        credential.username = encrypt(username, credential_key)
    if password:
        credential.password = encrypt(password, credential_key)
    if url:
        credential.url = encrypt(url, credential_key)
    if mnemonics:
        new_mnemonics = []
        # Check if any of the provided mnemonics already exist
        existing_mnemonics = session.query(Mnemonic.name).filter(Mnemonic.name.in_(mnemonics)).all()
        existing_mnemonic_names = {mnemonic.name for mnemonic in existing_mnemonics}

        for mnemonic in mnemonics:
            if mnemonic in existing_mnemonic_names:
                console.print(f"[yellow]Note: The mnemonic '{mnemonic}' already exists and cannot be reused for a new credential. Skipped![/yellow]")
            else:
                # Update the Credential.mnemonics list 
                pass
                

    session.commit()

    console.print(Panel(f"Credential '{credential.name}' updated successfully!", title="Success", style="bold green"))

    credential.print_on_screen(vault_key=vault_key)