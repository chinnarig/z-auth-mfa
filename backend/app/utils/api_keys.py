"""
Utility functions for API key management
"""
import secrets
import hashlib
from typing import Tuple


def generate_api_key() -> str:
    """
    Generate a secure random API key
    Format: zlavox_live_<32_hex_characters>
    Example: zlavox_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
    """
    random_bytes = secrets.token_bytes(32)
    hex_string = random_bytes.hex()
    return f"zlavox_live_{hex_string}"


def generate_test_api_key() -> str:
    """
    Generate a test API key for development/testing
    Format: zlavox_test_<32_hex_characters>
    """
    random_bytes = secrets.token_bytes(32)
    hex_string = random_bytes.hex()
    return f"zlavox_test_{hex_string}"


def hash_api_key(api_key: str) -> str:
    """
    Create a SHA-256 hash of an API key for secure storage comparison
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key_format(api_key: str) -> Tuple[bool, str]:
    """
    Verify that an API key has the correct format
    Returns: (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is required"
    
    if not api_key.startswith("zlavox_"):
        return False, "API key must start with 'zlavox_'"
    
    parts = api_key.split("_")
    if len(parts) != 3:
        return False, "Invalid API key format"
    
    prefix, env, key = parts
    if env not in ["live", "test"]:
        return False, "API key environment must be 'live' or 'test'"
    
    if len(key) != 64:  # 32 bytes = 64 hex characters
        return False, "Invalid API key length"
    
    return True, ""


def mask_api_key(api_key: str) -> str:
    """
    Mask an API key for display (show only first 15 and last 4 characters)
    Example: zlavox_live_a1b...o5p6
    """
    if not api_key or len(api_key) < 20:
        return "***"
    
    return f"{api_key[:15]}...{api_key[-4:]}"
