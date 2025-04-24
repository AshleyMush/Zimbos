"""
Utility functions for password hashing and verification.
"""
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """
    Hash a plaintext password for storing in the database.

    Args:
        password (str): The plaintext password.

    Returns:
        str: The hashed password.
    """
    return generate_password_hash(password)

def verify_password(stored_hash: str, password: str) -> bool:
    """
    Verify a plaintext password against the stored hash.

    Args:
        stored_hash (str): The stored password hash.
        password (str): The plaintext password to verify.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return check_password_hash(stored_hash, password)
