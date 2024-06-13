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
from password_manager.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

@click.command()
@click.argument('mnemonic', required=False)
@click.option('--uuid', help='UUID associated with the credential to update')
@click.option('-n', '--name', help='Updated name for the credential')
@click.option('-mn', '--mnemonics', multiple=True, help='Updated mnemonics for the credential')
@click.option('-u', '--username', help='Updated username for the credential')
@click.option('-url', '--url', help='Updated URL for the credential')
def update(mnemonic, uuid, name, mnemonics, username, url):
    """
    Update an existing credential in the database.

    This command updates various attributes of a credential in the password vault database.
    It can update the name, mnemonics, username, and URL associated with the credential.
    The password field cannot be updated using this command; use 'password-manager update-password'
    to update the password of a credential.

    Options:
        -mnemonic (str, optional): Mnemonic identifier of the credential to update.
        --uuid TEXT: UUID associated with the credential to update.
        -n, --name TEXT: Updated name for the credential.
        -mn, --mnemonics TEXT: Updated mnemonics for the credential (can be specified multiple times).
        -u, --username TEXT: Updated username for the credential.
        -url, --url TEXT: Updated URL for the credential.

    Examples:
        Update the name and username of a credential:
        $ password-manager update --uuid "123456" -n "New Credential Name" -u "new_username"

        Update mnemonics and URL for a credential whose mnemonic is 'facebook':
        $ password-manager update facebook -mn "new_mnemonic1" -mn "new_mnemonic2" -url "https://newurl.com"

        Update only the name of a credential identified by mnemonic 'twitter':
        $ password-manager update twitter -n "Updated Name"
    """
    print_basic_info()
    assert_db_init()
    
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
        console.print(f"[yellow]Credential not found with the provided identifier '{mnemonic or uuid}'. Update operation aborted.[/yellow]")
        return

    # Derive vault key
    vault_key = derive_vault_key(master_key=master_passwd)
    credential_key = credential.get_decrypted_key(vault_key=vault_key)

    # Update credential fields if provided
    if name:
        credential.name = name
    if username:
        credential.username = encrypt(username, credential_key)
    if url:
        credential.url = encrypt(url, credential_key)
    
    if mnemonics:
        new_mnemonics = []
        # Query all mnemonics whose credential_id is not equal to the current credential's id
        existing_mnemonics = session.query(Mnemonic.name).filter(
            Mnemonic.name.in_(mnemonics), Mnemonic.credential_id != credential.id
        ).all()
        existing_mnemonic_names = {mnemonic.name for mnemonic in existing_mnemonics}


        for mnemonic in set(mnemonics):
            if mnemonic in existing_mnemonic_names:
                console.print(f"[yellow]Note: The mnemonic '{mnemonic}' already exists and cannot be reused for a new credential. Skipped![/yellow]")
            else:
                new_mnemonics.append(mnemonic)

        # Delete existing mnemonics
        for mn in credential.mnemonics:
            session.delete(mn)
        
        session.commit()

        # Add new mnemonics
        for mnemonic in set(new_mnemonics):
            mnemonic_entry = Mnemonic(name=mnemonic, credential=credential)
            session.add(mnemonic_entry)

    session.commit()

    console.print(Panel(f"Credential '{credential.name}' updated successfully!", title="Success", style="bold green"))

    # Print the credential
    credential.print_on_screen(vault_key=vault_key, copy_to_clipboard=False)