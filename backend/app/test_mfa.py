#!/usr/bin/env python3
"""
Test script to verify MFA QR code and TOTP generation
Run this to test if your MFA setup will work correctly
"""

import pyotp
import qrcode
from io import BytesIO
import base64
import time

def test_mfa_setup():
    print("=" * 60)
    print("MFA Setup Test - Microsoft Authenticator Compatible")
    print("=" * 60)
    print()
    
    # Generate a test secret
    secret = pyotp.random_base32()
    print(f"✓ Generated Secret: {secret}")
    print()
    
    # Create TOTP instance
    totp = pyotp.TOTP(secret)
    
    # Generate provisioning URI
    test_email = "test@example.com"
    issuer = "VoiceAgent Platform"
    uri = totp.provisioning_uri(name=test_email, issuer_name=issuer)
    
    print(f"✓ Provisioning URI Generated:")
    print(f"  {uri}")
    print()
    
    # Format for manual entry
    manual_key = ' '.join([secret[i:i+4] for i in range(0, len(secret), 4)])
    print(f"✓ Manual Entry Key (formatted):")
    print(f"  {manual_key}")
    print()
    
    # Generate QR code
    print("✓ Generating QR Code...")
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to file for testing
    img.save("/tmp/test_qr_code.png")
    print(f"  QR Code saved to: /tmp/test_qr_code.png")
    print()
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG', optimize=True)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    data_url = f"data:image/png;base64,{img_str}"
    print(f"✓ Base64 Data URL length: {len(data_url)} characters")
    print()
    
    # Generate some test codes
    print("✓ Testing TOTP Code Generation:")
    print()
    
    for i in range(3):
        current_code = totp.now()
        time_remaining = 30 - (int(time.time()) % 30)
        
        print(f"  Code {i+1}: {current_code} (valid for {time_remaining}s)")
        
        # Verify the code works
        is_valid = totp.verify(current_code, valid_window=1)
        print(f"  Verification: {'✓ PASS' if is_valid else '✗ FAIL'}")
        print()
        
        if i < 2:
            print(f"  Waiting for next code...")
            time.sleep(31)  # Wait for new code
    
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print()
    print("To test with Microsoft Authenticator:")
    print("1. Open the QR code: /tmp/test_qr_code.png")
    print("2. Scan it with Microsoft Authenticator app")
    print("3. Or use manual entry with the key above")
    print("4. Compare the code in the app with the codes above")
    print()
    print("If codes match, your MFA setup is working correctly! ✓")
    print()

if __name__ == "__main__":
    try:
        test_mfa_setup()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()