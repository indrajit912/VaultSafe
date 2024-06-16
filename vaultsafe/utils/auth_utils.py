# /utils/auth_utils.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
#
import pwinput
import sys

import click
import itsdangerous
from itsdangerous import URLSafeTimedSerializer
from rich.console import Console
from rich.panel import Panel

from vaultsafe.db.models import session, Vault
from vaultsafe.config import DOT_SESSION_FILE

console = Console()

def get_password(
        info_msg: str = "Enter your password: ", 
        success_msg: str = "Password set successfully!", 
        warning_msg:str = "Passwords do not match. Please try again.\n", 
        confirmation_msg:str="Confirm your password: "
):
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
        password2 = pwinput.pwinput(confirmation_msg, mask=bullet_unicode)
        if password1 == password2:
            console.print(Panel(f"[bold green]{success_msg}[/bold green]", border_style="green"))
            return password1
        else:
            click.echo(warning_msg)

def _master_passwd_from_session(**kwargs):
    # Get the existing session token
    existing_token = get_existing_session_token()

    if existing_token:
        # Existing token found!
        # Confirm the session token and get the master_passwd
        master_passwd = confirm_session_token(
            token=existing_token,
            **kwargs
        )

        if not master_passwd:
            console.print(Panel("[bold red]Session token expired![/bold red]", border_style="red"))
        else:
            return master_passwd

def input_master_passwd_and_verify():
    """
    Take the master_passwd from user and verify it. If everything
    is ok then returns the user input.
    """
    bullet_unicode = '\u2022'

    vault = session.query(Vault).first()
    if not vault:
        console.print(Panel("[bold red]Vault not initialized. First use 'init' command to initialize a new Vault.[/bold red]", border_style="red"))
        sys.exit(1)

    # Check session if True
    if vault.session_check:
        master_passwd = _master_passwd_from_session(
            session_secret_key=vault.session_secret_key,
            session_salt=vault.session_salt,
            expiration=vault.session_expiration
        )
        if master_passwd:
            return master_passwd
    
    # Take master_passwd from user!
    master_passwd = pwinput.pwinput("Enter your master password: ", mask=bullet_unicode)

    # Check master_password
    if not vault.check_password(master_passwd):
        console.print(Panel("[bold red]Sorry, wrong password![/bold red]", border_style="red"))
        sys.exit(1)

    console.print(Panel("[bold green]Master password verified successfully![/bold green]", border_style="green"))

    # Generate a session token from the master_passwd
    new_session_token = generate_session_token(
        master_password=master_passwd,
        session_secret_key=vault.session_secret_key,
        session_salt=vault.session_salt
    )

    # Save the token to .session
    save_session_token(token=new_session_token)

    return master_passwd

def generate_session_token(master_password:str, session_secret_key:str, session_salt:str):
    """
    Generate a session token using the master password hash.
    
    :param master_passwd_hash: The hash of the user's master password.
    :return: The generated session token.
    """
    if isinstance(master_password, bytes):
        master_password = master_password.decode()

    serializer = URLSafeTimedSerializer(
        secret_key=session_secret_key, salt=session_salt
    )
    return serializer.dumps({'master_passwd': master_password})


def confirm_session_token(token: str, session_secret_key, session_salt, expiration):
    """
    Confirm the validity of a session token.
    
    :param token: The session token to be confirmed.
    :param expiration: The expiration time for the token in seconds (default 1 hour).
    :return: If the token is valid, return the decoded data, otherwise return None.
    """
    serializer = URLSafeTimedSerializer(
        secret_key=session_secret_key, salt=session_salt
    )

    try:
        data = serializer.loads(token, max_age=expiration)

        master_passwd = data.get('master_passwd')

        if master_passwd is not None:
            return master_passwd
        else:
            return None  # Invalid token structure

    except itsdangerous.SignatureExpired:
        return None  # Token expired

    except itsdangerous.BadSignature:
        return None  # Invalid token


def save_session_token(token:str):
    """Save the session token"""
    with open(DOT_SESSION_FILE, 'w') as f:
        f.write(token)

def get_existing_session_token():
    """Get the existing session token from the file"""
    if not DOT_SESSION_FILE.exists():
        return None
    
    with open(DOT_SESSION_FILE, 'r') as f:
        return f.read()