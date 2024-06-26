# models.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
#
import getpass
import uuid
import socket
from datetime import datetime

import pyperclip
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vaultsafe.utils.crypto_utils import sha256_hash, decrypt, generate_session_secret_key
from vaultsafe.utils.general_utils import utcnow, convert_utc_to_local_str
from vaultsafe.commands.generate_strong_passwd import generate_strong_password
from vaultsafe.config import DATABASE_URL

Base = declarative_base()

class Vault(Base):
    __tablename__ = 'vault'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, default=lambda: uuid.uuid4().hex)  # Optional, defaults to a generated UUID
    name = Column(String, default=lambda: socket.gethostname())  # Optional, defaults to system's hostname
    vault_key_hash = Column(String, nullable=False)
    master_password_hash = Column(String, nullable=False)
    date_created = Column(DateTime, default=utcnow)
    last_updated = Column(DateTime, default=utcnow, onupdate=utcnow)
    owner_name = Column(String, default=lambda: getpass.getuser())  # Optional, defaults to system's current user
    owner_email = Column(String)  # Optional

    password_salt = Column(String, nullable=False)
    session_check = Column(Boolean, nullable=False, default=True)
    session_secret_key = Column(String, nullable=False, default=generate_session_secret_key)
    session_salt = Column(String, nullable=False, default=generate_strong_password)
    session_expiration = Column(Integer, nullable=False, default=3 * 3600)

    def set_vault_key_hash(self, vault_key):
        """
        Sets the vault key hash from the provided vault key.

        Args:
            vault_key (bytes or str): The vault key to be hashed and stored.
        """
        self.vault_key_hash = sha256_hash(vault_key)

    def set_master_password_hash(self, master_password: str):
        """
        Sets the master password hash from the provided master password.

        Args:
            master_password (str): The master password to be hashed and stored.
        """
        self.password_salt = generate_strong_password(25)
        self.master_password_hash = sha256_hash(master_password + self.password_salt)

    def check_password(self, raw_password: str):
        """Checks whether the password is correct"""
        if sha256_hash(raw_password + self.password_salt) == self.master_password_hash:
            return True
        else:
            return False

    def json(self):
        """
        Serialize the Vault instance to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representation of the Vault instance.
        """
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "vault_key_hash": self.vault_key_hash,
            "master_password_hash": self.master_password_hash,
            "password_salt": self.password_salt,
            "date_created": self.date_created.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "owner_name": self.owner_name,
            "owner_email": self.owner_email,
            "session_expiration": self.session_expiration
        }
    
    def print_on_screen(self):
        """
        Prints the Vault information on the terminal screen in a professional CLI app style using rich library.
        """
        console = Console()

        table = Table(title="Vault Details", title_style="bold cyan", style="bright_blue")
        table.add_column("Field", style="bold")
        table.add_column("Value", justify="left")

        table.add_row("ID", str(self.id))
        table.add_row("UUID", self.uuid)
        table.add_row("Name", self.name)
        table.add_row("Owner", self.owner_name)
        table.add_row("Owner Email", self.owner_email if self.owner_email else '-')
        table.add_row("Date Created", convert_utc_to_local_str(self.date_created))
        table.add_row("Last Updated", convert_utc_to_local_str(self.last_updated))
        table.add_row("Vault Key Hash", self.vault_key_hash)
        table.add_row("Master Password Hash", self.master_password_hash)
        table.add_row("Session Check", str(self.session_check))
        if self.session_check:
            table.add_row("Session Expiration (in sec)", str(self.session_expiration))

        console.print(Panel(table, title=self.name, title_align="left", border_style="bright_blue"))


class Mnemonic(Base):
    __tablename__ = 'mnemonic'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    credential_id = Column(Integer, ForeignKey('credential.id'))
    credential = relationship('Credential', back_populates='mnemonics')

    def __str__(self):
        return f"Mnemonic(id={self.id}, name={self.name}, credential_id={self.credential_id})"

class Credential(Base):
    __tablename__ = 'credential'
    NONE_STR = "Not Provided"
    DEFAULT_ENCRYPTION_ALGO = "Fernet"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, default=lambda: uuid.uuid4().hex)  # Optional, defaults to a generated UUID

    name = Column(String, nullable=False)
    url = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    recovery_key = Column(String, nullable=True)

    primary_email = Column(String, nullable=True)
    secondary_email = Column(String, nullable=True)
    token = Column(String, nullable=True, default=None)
    notes = Column(Text, nullable=True)

    date_created = Column(DateTime, default=utcnow)
    last_updated = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Add encrypted_key attr. This key is used to encrypt username and password
    encrypted_key = Column(String, nullable=False)
    encryption_algorithm = Column(String, default=DEFAULT_ENCRYPTION_ALGO)

    mnemonics = relationship('Mnemonic', back_populates='credential', cascade='all, delete-orphan')

    def __str__(self):
        url_str = self._get_none_or_encrypted_str(self.url)
        username_str = self._get_none_or_encrypted_str(self.username)
        passwd_str = self._get_none_or_encrypted_str(self.password)

        return (
            "Credential("
            + "\n "
            + f"id={self.id}"
            + "\n "
            + f"uuid={self.uuid}"
            + "\n "
            + f"name={self.name}"
            + "\n "
            + f"url={url_str}"
            + "\n "
            + f"username={username_str}"
            + "\n "
            + f"password={passwd_str}"
            + "\n "
            + f"encrypted_key={self.encrypted_key}"
            + "\n)"
        )
    
    def get_decrypted_key(self, vault_key):
        """
        Returns the decrypted key that can be further used to decrypt all
        encrypted attributes in the Credential.

        Returns (bytes): decrypted_key
        """
        return decrypt(self.encrypted_key, vault_key)
    
    def json(self, vault_key=None):
        """
        Returns a JSON representation of the object, with optional decryption of attributes.

        If a `vault_key` is provided, it uses the `vault_key` to decrypt all relevant attributes.
        If no `vault_key` is provided, it returns the attributes as stored in the database.

        Args:
            vault_key (str, optional): Key used to decrypt the attributes. Defaults to None.

        Returns:
            dict: A dictionary containing the object's data, with decrypted attributes if a `vault_key` is provided.
        """
        def decrypt_attr(attr, key):
            return decrypt(attr, key) if attr else self.NONE_STR

        decrypted_data = {}
        if vault_key:
            # Get the decrypted_key
            credential_key = self.get_decrypted_key(vault_key=vault_key)

            decrypted_data = {
                'url': decrypt_attr(self.url, credential_key),
                'username': decrypt_attr(self.username, credential_key),
                'password': decrypt_attr(self.password, credential_key),
                'recovery_key': decrypt_attr(self.recovery_key, credential_key),
                'primary_email': decrypt_attr(self.primary_email, credential_key),
                'secondary_email': decrypt_attr(self.secondary_email, credential_key),
                'token': decrypt_attr(self.token, credential_key),
                'notes': decrypt_attr(self.notes, credential_key)
            }
        else:
            decrypted_data = {
                'url': self.url.decode() if self.url else self.NONE_STR,
                'username': self.username.decode() if self.username else self.NONE_STR,
                'password': self.password.decode() if self.password else self.NONE_STR,
                'recovery_key': self.recovery_key.decode() if self.recovery_key else self.NONE_STR,
                'primary_email': self.primary_email.decode() if self.primary_email else self.NONE_STR,
                'secondary_email': self.secondary_email.decode() if self.secondary_email else self.NONE_STR,
                'token': self.token.decode() if self.token else self.NONE_STR,
                'notes': self.notes.decode() if self.notes else self.NONE_STR
            }

        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            **decrypted_data,
            'mnemonics': [mn.name for mn in self.mnemonics],
            'encrypted_key': self.encrypted_key.decode(),
            'encryption_algorithm': self.encryption_algorithm,
            "date_created": self.date_created.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
            
    
    def print_on_screen(self, vault_key, **kwargs):
        self._print_on_screen(credential_data=self.json(vault_key), **kwargs)
    
    @staticmethod
    def _print_on_screen(credential_data, copy_to_clipboard:bool=True, count:int=None):
        """
        Prints the relevant info related to the Credential on the terminal screen for the user.

        Parameters:
        credential_data (dict): The dictionary containing credential information.
        copy_to_clipboard (bool): If True then the 'password' will be copied to the clipboard.
        """
        console = Console()

        count = "(" + str(count) + ") " if count else ''

        id = credential_data.get('id')
        uuid = credential_data.get('uuid')
        name = credential_data.get('name')
        url = credential_data.get('url')
        username = credential_data.get('username')
        password = credential_data.get('password')
        password_display = '\\[encrypted]' if password != Credential.NONE_STR else password
        recovery_key = credential_data.get('recovery_key')
        recovery_key_display = '\\[encrypted]' if recovery_key != Credential.NONE_STR else recovery_key

        primary_email = credential_data.get('primary_email')
        secondary_email = credential_data.get('secondary_email')
        token = credential_data.get('token')
        token_display = '\\[encrypted]' if token != Credential.NONE_STR else token
        notes = credential_data.get('notes')
        mnemonics:list = credential_data.get('mnemonics')

        dt_created_iso = credential_data.get('date_created')
        dt_created_str = convert_utc_to_local_str(datetime.fromisoformat(dt_created_iso))
        last_updated_iso = credential_data.get('last_updated')
        last_updated_str = convert_utc_to_local_str(datetime.fromisoformat(last_updated_iso))

        table = Table(show_header=True, header_style="bold cyan", border_style="bright_blue")
        table.add_column("Field", style="bold", justify="right")
        table.add_column("Value", style="bold magenta", justify="left")
        
        table.add_row("ID", f"[yellow]{id}[/yellow]")
        table.add_row("UUID", f"[green]{uuid}[/green]")
        table.add_row("URL", f"[bright_blue]{url}[/bright_blue]")
        table.add_row("Username", f"[bright_green]{username}[/bright_green]")
        table.add_row("Password", f"[red]{password_display}[/red]")
        table.add_row("Recovery Key", f"[red]{recovery_key_display}[/red]")
        table.add_row("Primary Email", f"[magenta]{primary_email}[/magenta]")
        table.add_row("Secondary Email", f"[magenta]{secondary_email}[/magenta]")
        table.add_row("Token", f"[red]{token_display}[/red]")
        

        if mnemonics:
            mnemonics_str = ", ".join(f"[cyan]{mnemonic}[/cyan]" for mnemonic in mnemonics)
            table.add_row("Mnemonics", mnemonics_str)

        table.add_row("Date Created", f"[red]{dt_created_str}[/red]")
        table.add_row("Last Updated", f"[red]{last_updated_str}[/red]")
        table.add_row("Notes", f"[magenta]{notes}[/magenta]")

        panel = Panel(table, title=count + name, title_align="left", border_style="bold magenta")

        console.print(panel)

        if copy_to_clipboard and password != Credential.NONE_STR:
            pyperclip.copy(password)

    
    @staticmethod
    def _get_none_or_encrypted_str(text:str):
        return 'None' if text is None else '[encrypted]'


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create a session
session = Session()
