# This script handles the export command.
# Author: Indrajit Ghosh
# Created On: Jun 14, 2024
# 
import json
import csv
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from vaultsafe.db.models import session, Credential
from vaultsafe.utils.auth_utils import input_master_passwd_and_verify
from vaultsafe.utils.crypto_utils import derive_vault_key
from vaultsafe.utils.cli_utils import assert_db_init, print_basic_info

console = Console()

# TODO: Encrypt the credential data before exporting with a password from user
# TODO: Add an attribute `data_encrypted` = True or False to interpret the fact that
# The data was encrypted before exporting.
# TODO: Accordingly modify the import_credential.
def export_credentials(credentials, vault_key, output_dir, file_format):
    """
    Export credentials to the specified file format.

    Parameters:
    - credentials (list): List of Credential objects.
    - vault_key (bytes): Key to decrypt credential attributes.
    - output_dir (str): Directory where the output file will be saved.
    - file_format (str): Output file format ('json', 'csv').
    """
    credentials_data = []
    
    for credential in credentials:
        credential_data = {}
        _cred_data_json = credential.json(vault_key=vault_key)

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

        credentials_data.append(credential_data)
    
    if file_format == 'json':
        output_file = Path(output_dir) / 'credentials.json'
        with open(output_file, 'w') as f:
            json.dump(credentials_data, f, indent=4)
        console.print(f"Exported credentials to [bold]{output_file}[/bold]")

    elif file_format == 'csv':
        output_file = Path(output_dir) / 'credentials.csv'
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=credentials_data[0].keys())
            writer.writeheader()
            writer.writerows(credentials_data)
        console.print(f"Exported credentials to [bold]{output_file}[/bold]")
    
    elif file_format == 'txt':
        output_file = Path(output_dir) / 'credentials.txt'
        with open(output_file, 'w') as f:
            for idx, cred in enumerate(credentials_data, start=1):
                f.write(f"Credential {idx}\n")
                f.write("=" * 20 + "\n")
                for key, value in cred.items():
                    f.write(f"{key.capitalize()}: {value if value is not None else 'N/A'}\n")
                f.write("\n")
        console.print(f"Exported credentials to [bold]{output_file}[/bold]")

    else:
        console.print("[bold red]Error:[/bold red] Invalid file format. Please choose 'json' or 'csv'.")

# TODO: Add an option `-e, --encrypt` with is_flag=True. If this flag is passed
# then input a password from uer and use that password to encrypt the content. 
@click.command()
@click.option('--output-dir', '-o', default=Path.home() / 'Downloads', type=click.Path(), help='Output directory for the exported file.')
@click.option('--file-format', '-f', type=click.Choice(['json', 'csv', 'txt']), default='json', 
              help='File format for export (json or csv). Default is json.')
def export(output_dir, file_format):
    """
    Export credentials to a specified file format.

    This command exports credentials from a database or another source to a file.
    The exported file can be in JSON or CSV format, depending on the chosen --file-format option.

    Options:
    -o, --output_dir (str): Directory where the exported file will be saved.
    -f, --file_format (str): File format for export ('json' or 'csv'). Defaults to 'json'.

    Example usage:
    \b
    $ vaultsafe export --output-dir /path/to/export --file-format csv
    """
    print_basic_info()
    assert_db_init()
    
    console.rule("Export Credentials")

    # Print warning message in a Panel with colored text
    warning_message = "[red]Please keep the exported file very safe, as it contains all your passwords in an unencrypted format.[/red]"
    rprint(Panel(warning_message, title="Security Warning", title_align="left", highlight=True, padding=1), '\n')


    # Take master password
    master_passwd = input_master_passwd_and_verify()
    
    # Derive the vault key
    vault_key = derive_vault_key(master_key=master_passwd)

    # Fetch credentials from the database or any other source
    credentials = session.query(Credential).all()

    if not credentials:
        console.print("[bold yellow]Warning:[/bold yellow] No credentials found to export.")
        return
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    export_credentials(credentials, vault_key, output_dir, file_format)

