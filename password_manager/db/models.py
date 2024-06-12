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

from password_manager.utils.auth import get_password
from password_manager.utils.cli import clear_terminal_screen
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

        # TODO: Take the `master_password` from user
        master_passwd = get_password(
            info_msg="[-] Enter a password for the app (e.g. your system passwd): ", 
            success_msg="  - Master password has been set successfully. Remember this password for future!"
        )
        print(master_passwd)

        # TODO: Generate the sha256 hash value of `master_key`

        # TODO: Derive `vault_key` from the `master_key`

        # TODO: Generate the sha256 has value of `vault_key`

        # TODO: Create a Vault() object and save it into the db

        print("Database initialized.")
    else:
        print("Database already exists.")
        res = input("[-] Do you want to delete all existing data and start afresh? (y/n): ")
        if res.lower() == 'y':
            shutil.rmtree(DOT_PASSWD_MANGR_DIR)
            print("Existing data deleted.")
            init_db()  # Call init_db again to recreate the database