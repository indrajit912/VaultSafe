# This script handles the export command.
# Author: Indrajit Ghosh
# Created On: Jun 14, 2024
# 
import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from vaultsafe.db.models import session, Credential
from vaultsafe.utils.auth_utils import input_master_passwd_and_verify, get_password
from vaultsafe.utils.crypto_utils import derive_vault_key, decrypt, encrypt, sha256_hash
from vaultsafe.utils.cli_utils import assert_db_init, print_basic_info
from vaultsafe.utils.general_utils import utcnow, convert_utc_to_local_str

console = Console()


def export_credentials(credentials, output_dir, file_format, vault_key, file_key=None):
    """
    Export credentials to the specified file format.

    Parameters:
    - credentials (list): List of Credential objects.
    - vault_key (bytes): Key to decrypt credential attributes.
    - output_dir (str): Directory where the output file will be saved.
    - file_format (str): Output file format ('json', 'txt').
    """
    credentials_data = []

    file_encrypted = True if file_key else False
    
    for credential in credentials:
        credential_data = {}
        _cred_data_json = credential.json() if file_key else credential.json(vault_key=vault_key)

        credential_data['id'] = _cred_data_json['id']
        credential_data['uuid'] = _cred_data_json['uuid']
        credential_data['name'] = _cred_data_json['name']
        credential_data['mnemonics'] = ', '.join(_cred_data_json['mnemonics'])
        credential_data['url'] = None if _cred_data_json['url'] == Credential.NONE_STR else _cred_data_json['url']
        credential_data['username'] = None if _cred_data_json['username'] == Credential.NONE_STR else _cred_data_json['username']
        credential_data['password'] = None if _cred_data_json['password'] == Credential.NONE_STR else _cred_data_json['password']
        credential_data['recovery_key'] = None if _cred_data_json['recovery_key'] == Credential.NONE_STR else _cred_data_json['recovery_key']
        credential_data['primary_email'] = None if _cred_data_json['primary_email'] == Credential.NONE_STR else _cred_data_json['primary_email']
        credential_data['secondary_email'] = None if _cred_data_json['secondary_email'] == Credential.NONE_STR else _cred_data_json['secondary_email']
        credential_data['token'] = None if _cred_data_json['token'] == Credential.NONE_STR else _cred_data_json['token']
        credential_data['notes'] = None if _cred_data_json['notes'] == Credential.NONE_STR else _cred_data_json['notes']

        if file_key:
            # Get the encrypted credential key
            credential_key_encrypted = _cred_data_json['encrypted_key'].encode()

            # Decrypt the credential's encrypted_key
            credential_key = decrypt(credential_key_encrypted, vault_key)

            # Encrypt the credential key using the file_key
            cred_key_encrypted_by_file_key = encrypt(credential_key, file_key)

            credential_data['encrypted_key'] = cred_key_encrypted_by_file_key.decode()

        credentials_data.append(credential_data)

    current_timestamp = convert_utc_to_local_str(dt=utcnow())
    
    metadata = {
        'file_encrypted': file_encrypted,
        'exported_date': current_timestamp
    }

    if file_key:
        metadata['file_key_hash'] = sha256_hash(file_key)

    if file_format == 'json':
        output_data = {
            'metadata': metadata,
            'credentials': credentials_data
        }
        output_file = Path(output_dir) / 'credentials.json'
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=4)
        console.print(f"Exported credentials to [bold]{output_file}[/bold]")
    
    elif file_format == 'txt':
        output_file = Path(output_dir) / 'credentials.txt'
        with open(output_file, 'w') as f:
            f.write(f"File Encrypted: {metadata['file_encrypted']}\n")
            f.write(f"Exported Date: {metadata['exported_date']}\n")
            if file_key:
                f.write(f"File Key SHA256 Hash: {metadata['file_key_hash']}\n")
            f.write("=" * 58 + "\n\n")
            for idx, cred in enumerate(credentials_data, start=1):
                f.write(f"Credential {idx}\n")
                f.write("=" * 20 + "\n")
                for key, value in cred.items():
                    f.write(f"{key.capitalize()}: {value if value is not None else 'N/A'}\n")
                f.write("\n")
        console.print(f"Exported credentials to [bold]{output_file}[/bold]")

    else:
        console.print("[bold red]Error:[/bold red] Invalid file format. Please choose 'json' or 'txt'.")

@click.command()
@click.option('--output-dir', '-o', default=Path.home() / 'Downloads', type=click.Path(), help='Output directory for the exported file.')
@click.option('--file-format', '-f', type=click.Choice(['json', 'txt']), default='json', 
              help='File format for export (json or txt). Default is json.')
@click.option('-d', '--decrypt', is_flag=True, help='Export the data as decrypted. If not set, data will be exported as encrypted.')
def export(output_dir, file_format, decrypt):
    """
    Export credentials to a specified file format.

    This command exports credentials from a database or another source to a file.
    The exported file can be in JSON or TXT format, depending on the chosen --file-format option.

    Note: Please choose the 'json' file format if you intend to import the file back into the 
        application in the future. A 'txt' file cannot be imported.

    Options:
    -o, --output_dir (str): Directory where the exported file will be saved.
    -f, --file_format (str): File format for export ('json' or 'txt'). Defaults to 'json'.

    Flag:
    -d, --decrypt : If this flag is given then the data will be exported as decrypted form.

    Example usage:
    \b
    $ vaultsafe export --output-dir /path/to/export --file-format txt
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("Export Credentials")

    # Take master password
    master_passwd = input_master_passwd_and_verify()

    # Fetch credentials from the database or any other source
    credentials = session.query(Credential).all()

    if not credentials:
        console.print("[bold yellow]Warning:[/bold yellow] No credentials found to export.")
        return
    
    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)


    if decrypt:
        # Print warning message in a Panel with colored text
        warning_message = "[red]Please keep the exported file very safe, as it contains all your passwords in an unencrypted format.[/red]"
        rprint(Panel(warning_message, title="Security Warning", title_align="left", highlight=True, padding=1), '\n')

        file_key = None
        
    else:
        # The data will be exported as encrypted format.
        
        # Ask the user for a file password that can be used to decrypt the exported data in future.
        file_passwd = get_password(
            info_msg="The exported file will be encrypted using an algorithm.\nPlease enter a file password that can be used to recover all your data during future imports: ",
            success_msg="The exported file is encrypted with this password for security. Please remember this password, as it will be required during import."
        )

        # Derive a key to encrypt the credential key
        file_key = derive_vault_key(master_key=file_passwd)

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    export_credentials(
        credentials=credentials,
        output_dir=output_dir,
        file_format=file_format,
        vault_key=vault_key,
        file_key=file_key
    )

