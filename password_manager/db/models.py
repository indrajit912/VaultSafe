# models.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
#
import shutil

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from password_manager.utils.auth_utils import get_password
from password_manager.utils.crypto_utils import sha256_hash, derive_vault_key
from password_manager.utils.cli_utils import clear_terminal_screen
from config import DATABASE_PATH, DATABASE_URL, DOT_PASSWD_MANGR_DIR

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
    vault_key_hash = Column(String, nullable=False)
    master_password_hash = Column(String, nullable=False)
    date_created = Column(DateTime, default=utcnow)
    last_updated = Column(DateTime, default=utcnow, onupdate=utcnow)

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
        self.master_password_hash = sha256_hash(master_password)


class Mnemonic(Base):
    __tablename__ = 'mnemonic'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    credential_id = Column(Integer, ForeignKey('credential.id'))
    credential = relationship('Credential', back_populates='mnemonics')

class Credential(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    # TODO: Add encrypted_key attr

    mnemonics = relationship('Mnemonic', back_populates='credential', cascade='all, delete-orphan')

    @validates('mnemonics')
    def validate_mnemonics(self, key, mnemonic):
        if not self.mnemonics:
            raise ValueError("Each Credential must have at least one Mnemonic.")
        return mnemonic

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def init_db():
    if not DATABASE_PATH.exists():
        clear_terminal_screen()
        
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(engine)

        # Take the `master_password` from user
        master_passwd = get_password(
            info_msg="[-] Enter a password for the app (e.g. your system passwd): ", 
            success_msg="  - Master password set successfully. Please remember this password for future use!"
        )

        # Create a session
        session = Session()

        # Create a Vault instance
        vault = Vault()

        # Set the sha256 hash value of `master_key`
        vault.set_master_password_hash(master_password=master_passwd)

        # Derive `vault_key` from the `master_key`
        vault_key = derive_vault_key(master_key=master_passwd)

        # Set the sha256 has value of `vault_key`
        vault.set_vault_key_hash(vault_key=vault_key)

        # Add the vault instance to the session and commit it to the database
        session.add(vault)
        session.commit()

        # Clear the screen
        clear_terminal_screen()

        print("Database initialized.")

        # Print the hashes to verify
        print(f"Master Password Hash: {vault.master_password_hash}")
        print(f"Vault Key Hash: {vault.vault_key_hash}")
    else:
        print("Database already exists.")
        res = input("[-] Do you want to delete all existing data and start afresh? (y/n): ")
        if res.lower() == 'y':
            shutil.rmtree(DOT_PASSWD_MANGR_DIR)
            print("Existing data deleted.")
            init_db()  # Call init_db again to recreate the database