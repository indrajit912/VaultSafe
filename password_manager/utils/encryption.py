# /utils/encryption.py

import hashlib

def sha256_hash(data):
    """Creates a SHA-256 hash of the input data."""
    sha256_hash = hashlib.sha256(data.encode()).hexdigest()
    return sha256_hash


def derive_key(master_key, key_length=32, iterations=100000):
    """Derives a key from the master key using PBKDF2."""
    salt = "salt-for-key-derivation-from-master-key"
    key = hashlib.pbkdf2_hmac('sha256', master_key.encode(), salt, iterations, dklen=key_length)
    return key