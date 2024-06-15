# This script handles the update command.
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
@click.argument('mnemonic', required=False)
@click.option('--uuid', help='UUID associated with the credential to update')
@click.option('-n', '--name', help='Updated name for the credential')
@click.option('-mn', '--mnemonics', multiple=True, help='Updated mnemonics for the credential')
@click.option('-u', '--username', help='Updated username for the credential')
@click.option('-p', '--password', is_flag=True, help="Flag to update the password.")
@click.option('-t', '--token', is_flag=True, help="Flag to update the token.")
@click.option('-k', '--recovery-key', is_flag=True, help="Flag to update the recovery key.")
@click.option('-pe', '--primary-email', required=False, help='Primary email id associated with the credential')
@click.option('-se', '--secondary-email', required=False, help='Secondary email id associated with the credential')
@click.option('-url', '--url', help='Updated URL for the credential')
@click.option('-nt', '--notes', required=False, help='Notes that could be stored along with the credential')
def update(mnemonic, uuid, name, mnemonics, username, password, token, recovery_key, url, primary_email, secondary_email, notes):
    """
    Update an existing credential in the database.

    This command updates various attributes of a credential in the password vault database.
    It can update the name, mnemonics, username, primary email, secondary email, URL, and notes 
    associated with the credential. The password, token, and recovery key can also be updated 
    using their respective flags.

    Arguments:
        mnemonic (str, optional): Mnemonic identifier of the credential to update.

    Options:
        --uuid TEXT: UUID associated with the credential to update.
        -n, --name TEXT: Updated name for the credential.
        -mn, --mnemonics TEXT: Updated mnemonics for the credential (can be specified multiple times).
        -u, --username TEXT: Updated username for the credential.
        -p, --password: Flag to update the password.
        -t, --token: Flag to update the token.
        -k, --recovery-key: Flag to update the recovery key.
        -pe, --primary-email TEXT: Primary email id associated with the credential.
        -se, --secondary-email TEXT: Secondary email id associated with the credential.
        -url, --url TEXT: Updated URL for the credential.
        -nt, --notes TEXT: Write any notes related to the credential (optional).

    Examples:
        Update the name and username of a credential:
        $ password-manager update --uuid "123456" -n "New Credential Name" -u "new_username"

        Update mnemonics and URL for a credential whose mnemonic is 'facebook':
        $ password-manager update facebook -mn "new_mnemonic1" -mn "new_mnemonic2" -url "https://newurl.com"

        Update only the name of a credential identified by mnemonic 'twitter':
        $ password-manager update twitter -n "Updated Name"

        Update primary and secondary emails for a credential:
        $ password-manager update --uuid "123456" -pe "primary@example.com" -se "secondary@example.com"

        Add notes to a credential identified by mnemonic 'linkedin':
        $ password-manager update linkedin -nt "These are some notes related to the credential."

        Update the password of a credential:
        $ password-manager update twitter -p

        Update the token of a credential:
        $ password-manager update facebook -t

        Update the recovery key of a credential:
        $ password-manager update linkedin -k
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
    if primary_email:
        credential.primary_email = encrypt(primary_email, credential_key)
    if secondary_email:
        credential.secondary_email = encrypt(secondary_email, credential_key)
    if notes:
        credential.notes = notes

    # Update password if flag is provided
    if password:
        new_password = get_password(
            info_msg="Give the new password for the credential: ",
            success_msg="Passwords matched!"
        )
        new_password_encrypted = encrypt(new_password, credential_key)
        credential.password = new_password_encrypted
        console.print(Panel("[bold green]Credential's password changed successfully![/bold green]", style="bold green"))
    
    # Update token if flag is provided
    if token:
        new_token = get_password(
            info_msg="Enter the new token: ",
            success_msg="Tokens matched!"
        )
        new_token_encrypted = encrypt(new_token, credential_key)
        credential.token = new_token_encrypted
        console.print(Panel("[bold green]Credential's token changed successfully![/bold green]", style="bold green"))

    # Update recovery key if flag is provided
    if recovery_key:
        new_recovery_key = click.prompt("Enter the new recovery key", hide_input=True, confirmation_prompt=True)
        new_recovery_key = get_password(
            info_msg="Enter the new recovery key: ",
            success_msg="Recovery keys matched!"
        )
        new_recovery_key_encrypted = encrypt(new_recovery_key, credential_key)
        credential.recovery_key = new_recovery_key_encrypted
        console.print(Panel("[bold green]Credential's recovery key changed successfully![/bold green]", style="bold green"))
    
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