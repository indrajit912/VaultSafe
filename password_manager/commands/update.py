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
from password_manager.utils.cli_utils import assert_db_init

console = Console()

@click.command()
@click.argument('mnemonic', required=False)
@click.option('--uuid', help='UUID associated with the credential to update')
@click.option('-n', '--name', help='Updated name for the credential')
@click.option('-mn', '--mnemonics', multiple=True, help='Updated mnemonics for the credential')
@click.option('-u', '--username', help='Updated username for the credential')
@click.option('-p', '--password', help='Updated password for the credential')
@click.option('-url', '--url', help='Updated URL for the credential')
def update(mnemonic, uuid, name, mnemonics, username, password, url):
    """
    Update an existing credential in the database.

    This command allows updating various fields of a credential identified by either 'mnemonic' or 'uuid'.
    At least one of these identifiers must be provided.

    Args:
        mnemonic (str, optional): The mnemonic associated with the credential to update.
        uuid (str, optional): The UUID associated with the credential to update.
        name (str, optional): Updated name for the credential.
        mnemonics (list, optional): Updated mnemonics associated with the credential.
        username (str, optional): Updated username for the credential.
        password (str, optional): Updated password for the credential.
        url (str, optional): Updated URL for the credential.

    Notes:
        - If 'mnemonics' are provided, existing mnemonics associated with the credential will be replaced.
        - The command requires the database to be initialized ('init' command).

    Examples:
        To update a credential by mnemonic:
        \b
        $ password-manager update my_mnemonic -n "New Name" -u new_username

        To update a credential by UUID:
        \b
        $ password-manager update --uuid <UUID> -p new_password

    """
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
    if password:
        credential.password = encrypt(password, credential_key)
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