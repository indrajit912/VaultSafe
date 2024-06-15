# /utils/crypto_utils.py
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
#

import hashlib
import base64
from cryptography.fernet import Fernet

def sha256_hash(data: str):
    """
    Creates a SHA-256 hash of the input data.

    Args:
        data (str): The input data to be hashed. Can be a string or bytes.

    Returns:
        str: The SHA-256 hash of the input data in hexadecimal format.
    """
    if isinstance(data, bytes):
        sha256_hash = hashlib.sha256(data).hexdigest()
    else:
        sha256_hash = hashlib.sha256(data.encode()).hexdigest()
    return sha256_hash


def derive_vault_key(master_key: str, key_length: int = 32, iterations: int = 100000):
    """
    Derives a `vault_key` from the master key using PBKDF2 and encodes it in URL-safe base64 format.

    Args:
        master_key (str): The master key from which the derived key will be generated.
        key_length (int): The length of the derived key in bytes. Default is 32.
        iterations (int): The number of iterations for the PBKDF2 algorithm. Default is 100000.

    Returns:
        bytes: The derived key as a URL-safe base64-encoded bytes object.
    """
    salt = "salt-for-key-derivation-from-master-key".encode()  # Ensure the salt is in bytes
    key = hashlib.pbkdf2_hmac('sha256', master_key.encode(), salt, iterations, dklen=key_length)
    encoded_key = base64.urlsafe_b64encode(key)
    return encoded_key


def generate_fernet_key():
    """
    Generates a new Fernet key for encryption and decryption.

    Returns:
        bytes: The generated Fernet key.
    """
    return Fernet.generate_key()


def encrypt(data, key):
    """
    Encrypts the input data using the provided Fernet key.

    Args:
        data (str or bytes): The raw data to encrypt.
        key (bytes or str): The Fernet key for encryption.

    Returns:
        bytes: The encrypted data.
    """
    fernet = Fernet(key)
    if isinstance(data, str):
        data = data.encode()

    encrypted_data = fernet.encrypt(data)
    return encrypted_data


def decrypt(encrypted_data: bytes, key):
    """
    Decrypts the encrypted data using the provided Fernet key.

    Args:
        encrypted_data (bytes): The encrypted data to decrypt.
        key (bytes or str): The Fernet key for decryption.

    Returns:
        str: The decrypted raw data.
    """
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data