# This script handles the update command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
# 
import click
from rich.console import Console
from rich.panel import Panel

from password_manager.db.models import session, Credential, Mnemonic
from password_manager.utils.auth_utils import input_master_passwd_and_verify, get_password
from password_manager.utils.crypto_utils import derive_vault_key, encrypt, decrypt
from password_manager.utils.cli_utils import assert_db_init, print_basic_info, multiline_input

console = Console()

@click.command()
@click.argument('mnemonic', required=True)
@click.option('-n', '--name', is_flag=True, help='Flag to update name for the credential')
@click.option('-mn', '--mnemonics', is_flag=True, help='Flag to update mnemonics for the credential')
@click.option('-u', '--username', is_flag=True, help='Flag to update username for the credential')
@click.option('-pw', '--password', is_flag=True, help="Flag to update the password.")
@click.option('-tk', '--token', is_flag=True, help="Flag to update the token.")
@click.option('-rk', '--recovery-key', is_flag=True, help="Flag to update the recovery key.")
@click.option('-pe', '--primary-email', is_flag=True, help='Flag to update Primary email id associated with the credential')
@click.option('-se', '--secondary-email', is_flag=True, help='Flag to update Secondary email id associated with the credential')
@click.option('-url', '--url', is_flag=True, help='Flag to update URL for the credential')
@click.option('-nt', '--notes', is_flag=True, help='Flag to update notes stored along with the credential')
def update(mnemonic, name, mnemonics, username, password, token, recovery_key, url, primary_email, secondary_email, notes):
    """
    Update an existing credential in the database.

    This command updates various attributes of a credential in the password vault database.
    It can update the name, mnemonics, username, primary email, secondary email, URL, and notes 
    associated with the credential. The password, token, and recovery key can also be updated 
    using their respective flags.

    Arguments:
        mnemonic (str, required): Mnemonic identifier of the credential to update.

    Options:
        -n, --name: Flag to update the name for the credential.
        -mn, --mnemonics: Flag to update the mnemonics for the credential.
        -u, --username: Flag to update the username for the credential.
        -pw, --password: Flag to update the password.
        -tk, --token: Flag to update the token.
        -rk, --recovery-key: Flag to update the recovery key.
        -pe, --primary-email: Flag to update the primary email associated with the credential.
        -se, --secondary-email: Flag to update the secondary email associated with the credential.
        -url, --url: Flag to update the URL for the credential.
        -nt, --notes: Flag to update notes stored along with the credential.

    Examples:
        Update the name and username of a credential:
        $ password-manager update facebook -n -u

        Update mnemonics and URL for a credential whose mnemonic is 'twitter':
        $ password-manager update twitter -mn -url

        Update only the name of a credential identified by mnemonic 'linkedin':
        $ password-manager update linkedin -n

        Update primary and secondary emails for a credential:
        $ password-manager update google -pe -se

        Update notes of a credential identified by mnemonic 'amazon':
        $ password-manager update amazon -nt

        Update the password of a credential:
        $ password-manager update microsoft -pw

        Update the token of a credential:
        $ password-manager update github -tk

        Update the recovery key of a credential:
        $ password-manager update dropbox -rk
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("Update Credential")

    # Take master password
    master_passwd = input_master_passwd_and_verify()

    # Query credential based on mnemonic
    credential = session.query(Credential).join(Mnemonic).filter(Mnemonic.name == mnemonic).first()

    if not credential:
        console.print(f"[yellow]Credential not found with the provided identifier '{mnemonic}'. Update operation aborted.[/yellow]")
        return

    # Derive vault key
    vault_key = derive_vault_key(master_key=master_passwd)
    credential_key = credential.get_decrypted_key(vault_key=vault_key)

    # Display existing values before updating
    if name:
        console.print(f"Existing name: [bold]{credential.name}[/bold]")
        new_name = click.prompt("Enter the new name for the credential")
        credential.name = new_name
    if username:
        existing_username = decrypt(credential.username, credential_key) if credential.username else ""
        console.print(f"Existing username: [bold]{existing_username}[/bold]")
        new_username = click.prompt("Enter the new username for the credential")
        credential.username = encrypt(new_username, credential_key)

    # Update password if flag is provided
    if password:
        new_password = get_password(
            info_msg="Give the new password for the credential: ",
            success_msg="Passwords matched!"
        )
        new_password_encrypted = encrypt(new_password, credential_key)
        credential.password = new_password_encrypted
        console.print(Panel("[bold green]Credential's password changed successfully![/bold green]", style="bold green"))
    
    if url:
        existing_url = decrypt(credential.url, credential_key) if credential.url else ""
        console.print(f"Existing URL: [bold]{existing_url}[/bold]")
        new_url = click.prompt("Enter the new URL for the credential")
        credential.url = encrypt(new_url, credential_key)
    if primary_email:
        existing_primary_email = decrypt(credential.primary_email, credential_key) if credential.primary_email else ""
        console.print(f"Existing primary email: [bold]{existing_primary_email}[/bold]")
        new_pe = click.prompt("Enter the new 'primary email id' for the credential")
        credential.primary_email = encrypt(new_pe, credential_key)
    if secondary_email:
        existing_secondary_email = decrypt(credential.secondary_email, credential_key) if credential.secondary_email else ""
        console.print(f"Existing secondary email: [bold]{existing_secondary_email}[/bold]")
        new_se = click.prompt("Enter the new 'secondary email id' for the credential")
        credential.secondary_email = encrypt(new_se, credential_key)
        
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
        new_recovery_key = get_password(
            info_msg="Enter the new recovery key: ",
            success_msg="Recovery keys matched!"
        )
        new_recovery_key_encrypted = encrypt(new_recovery_key, credential_key)
        credential.recovery_key = new_recovery_key_encrypted
        console.print(Panel("[bold green]Credential's recovery key changed successfully![/bold green]", style="bold green"))

    if mnemonics:
        existing_mnemonics = " ".join([mnemonic.name for mnemonic in credential.mnemonics])
        console.print(f"Existing mnemonics: [bold]{existing_mnemonics}[/bold]")
        given_mnemonics = click.prompt("Enter the new set of mnemonics separated by white spaces (e.g mn1 mn2 mn3)")
        
        # Split the input into a list of mnemonics
        mnemonics = given_mnemonics.split()

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


    if notes:
        existing_notes = decrypt(credential.notes, credential_key) if credential.notes else ""
        new_notes = multiline_input(f"Existing notes:\n{existing_notes}\n\nUpdate the notes below. ([red]end with three empty lines[/red]):")
        credential.notes = encrypt(new_notes, credential_key)

    session.commit()

    console.print(Panel(f"Credential '{credential.name}' updated successfully!", title="Success", style="bold green"))

    # Print the credential
    credential.print_on_screen(vault_key=vault_key, copy_to_clipboard=False)
