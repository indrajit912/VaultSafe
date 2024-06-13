# models.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
#
import getpass
import uuid
import pyperclip
import socket
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from password_manager.utils.crypto_utils import sha256_hash, decrypt
from config import DATABASE_URL

Base = declarative_base()

def utcnow():
    """
    Get the current UTC datetime.

    Returns:
        datetime: A datetime object representing the current UTC time.
    """
    return datetime.now(timezone.utc)

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

    password_salt = "this-is-a-very-strong-salt-for-strengthen-master-password"

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
        self.master_password_hash = sha256_hash(master_password + self.password_salt)

    def check_password(self, raw_password: str):
        """Checks whether the password is correct"""
        if sha256_hash(raw_password + self.password_salt) == self.master_password_hash:
            # TODO: Derive the vault_key

            # TODO: Save vault_key to the `.session`

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
            "date_created": self.date_created.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "owner_name": self.owner_name,
            "owner_email": self.owner_email
        }
    
    def print_on_screen(self):
        """
        Prints the Vault information on the terminal screen in a professional CLI app style using rich library.
        """
        console = Console()

        table = Table(title="Vault Information", title_style="bold cyan", style="bright_blue")
        table.add_column("Field", style="bold")
        table.add_column("Value", justify="left")

        table.add_row("ID", str(self.id))
        table.add_row("UUID", self.uuid)
        table.add_row("Name", self.name)
        table.add_row("Owner", self.owner_name)
        table.add_row("Owner Email", self.owner_email if self.owner_email else '-')
        table.add_row("Date Created", self.date_created.strftime('%Y-%m-%d %H:%M:%S'))
        table.add_row("Last Updated", self.last_updated.strftime('%Y-%m-%d %H:%M:%S'))
        table.add_row("Vault Key Hash", self.vault_key_hash)
        table.add_row("Master Password Hash", self.master_password_hash)

        console.print(Panel(table, title="Vault Details", title_align="left", border_style="bright_blue"))


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
    id = Column(Integer, primary_key=True)
    uuid = Column(String, default=lambda: uuid.uuid4().hex)  # Optional, defaults to a generated UUID

    name = Column(String, nullable=False)
    url = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    
    # Add encrypted_key attr. This key is used to encrypt username and password
    encrypted_key = Column(String, nullable=False)

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
    
    def json(self, vault_key):
        """
        It uses the `vault_key` to decrypt all attributes and then 
        returns a json equivalent.
        """
        # Get the decrypted_key
        credential_key = self.get_decrypted_key(vault_key=vault_key)

        # Decrypt attributes
        url_decrypted = decrypt(self.url, credential_key) if self.url else self.NONE_STR
        username_decrypted = decrypt(self.username, credential_key) if self.username else self.NONE_STR
        passwd_decrypted = decrypt(self.password, credential_key) if self.password else self.NONE_STR

        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'url': url_decrypted,
            'username': username_decrypted,
            'password': passwd_decrypted,
            'mnemonics': [mn.name for mn in self.mnemonics],
            'key': self.encrypted_key
        }
    
    @staticmethod
    def print_on_screen(credential_data, copy_to_clipboard:bool=True, count:int=None):
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
        mnemonics:list = credential_data.get('mnemonics')

        table = Table(show_header=True, header_style="bold cyan", border_style="bright_blue")
        table.add_column("Field", style="bold", justify="right")
        table.add_column("Value", style="bold magenta", justify="left")

        table.add_row("ID", f"[yellow]{id}[/yellow]")
        table.add_row("UUID", f"[green]{uuid}[/green]")
        table.add_row("URL", f"[blue]{url}[/blue]")
        table.add_row("Username", f"[blue]{username}[/blue]")
        table.add_row("Password", f"[red]{password_display}[/red]")

        if mnemonics:
            mnemonics_str = ", ".join(f"[cyan]{mnemonic}[/cyan]" for mnemonic in mnemonics)
            table.add_row("Mnemonics", mnemonics_str)

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
