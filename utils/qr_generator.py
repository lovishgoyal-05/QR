import qrcode
import os
from pathlib import Path

# Ensure static directory exists
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def generate_qr_code(data: str, filename: str) -> str:
    """
    Generate a QR code from the given data and save it as a PNG file.
    Returns the public URL to access the QR code image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the file
    filepath = STATIC_DIR / f"{filename}.png"
    img.save(str(filepath))
    
    # Return the URL path
    return f"/static/{filename}.png"
