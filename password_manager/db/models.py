# models.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
#
import getpass
import uuid
import socket
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from password_manager.utils.crypto_utils import sha256_hash, generate_fernet_key, encrypt, decrypt
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


class Mnemonic(Base):
    __tablename__ = 'mnemonic'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    credential_id = Column(Integer, ForeignKey('credential.id'))
    credential = relationship('Credential', back_populates='mnemonics')

class Credential(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, default=lambda: uuid.uuid4().hex)  # Optional, defaults to a generated UUID

    name = Column(String, nullable=False)
    url = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    
    # Add encrypted_key attr. This key is used to encrypt username and password
    encrypted_key = Column(String, nullable=False)

    mnemonics = relationship('Mnemonic', back_populates='credential', cascade='all, delete-orphan')

    def get_decrypted_key(self, vault_key):
        """
        Returns the decrypted key that can be further used to decrypt all
        encrypted attributes in the Credential.

        Returns (bytes): decrypted_key
        """
        return decrypt(self.encrypted_key, vault_key)


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create a session
session = Session()
