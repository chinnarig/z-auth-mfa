import pyotp
import qrcode
from io import BytesIO
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
from dotenv import load_dotenv
import json

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
MFA_ISSUER_NAME = os.getenv("MFA_ISSUER_NAME", "VoiceAgent Platform")


def get_encryption_key() -> bytes:
    """Derive encryption key from SECRET_KEY"""
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'voice_agent_mfa_salt',  # In production, use a proper salt from env
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))
    return key


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data like MFA secrets"""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return ""
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(encrypted_data.encode())
    return decrypted.decode()


def generate_mfa_secret() -> str:
    """Generate a random base32 secret for TOTP"""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Generate provisioning URI for authenticator apps"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=email,
        issuer_name=MFA_ISSUER_NAME
    )


def generate_qr_code(uri: str) -> str:
    """Generate QR code image and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def verify_totp_code(secret: str, code: str) -> bool:
    """Verify a TOTP code against the secret"""
    try:
        totp = pyotp.TOTP(secret)
        # Allow 1 period (30 seconds) time drift in either direction
        return totp.verify(code, valid_window=1)
    except Exception:
        return False


def encrypt_backup_codes(codes: list[str]) -> str:
    """Encrypt backup codes for storage"""
    codes_json = json.dumps(codes)
    return encrypt_data(codes_json)


def decrypt_backup_codes(encrypted_codes: str) -> list[str]:
    """Decrypt backup codes from storage"""
    if not encrypted_codes:
        return []
    codes_json = decrypt_data(encrypted_codes)
    return json.loads(codes_json)


def verify_backup_code(encrypted_codes: str, code: str) -> tuple[bool, str]:
    """
    Verify a backup code and remove it from the list
    Returns: (is_valid, updated_encrypted_codes)
    """
    codes = decrypt_backup_codes(encrypted_codes)
    
    # Normalize the code (remove hyphens and convert to uppercase)
    normalized_code = code.replace("-", "").upper()
    
    for stored_code in codes:
        normalized_stored = stored_code.replace("-", "").upper()
        if normalized_stored == normalized_code:
            # Remove the used code
            codes.remove(stored_code)
            # Return updated encrypted codes
            return True, encrypt_backup_codes(codes)
    
    return False, encrypted_codes


def format_secret_for_manual_entry(secret: str) -> str:
    """Format secret in groups of 4 for easier manual entry"""
    return ' '.join([secret[i:i+4] for i in range(0, len(secret), 4)])
