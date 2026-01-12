"""
Script to create a simple image for Challenge 6 (Steganography).
This creates a basic PNG image that can be used for the challenge.
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a simple image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some text (the flag is also in the filename/metadata)
    text = "Thaghrah Challenge 6"
    try:
        # Try to use a default font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 80), text, fill='black', font=font)
    draw.text((50, 120), "Check the filename!", fill='gray', font=font)
    
    # Save the image
    os.makedirs('static/images', exist_ok=True)
    img.save('static/images/hidden_message.png')
    
    print("Image created successfully at static/images/hidden_message.png")
    print("Note: The flag 'IMAGE_STEGANOGRAPHY_FLAG' should be checked in browser dev tools or filename")
    
except ImportError:
    print("Pillow (PIL) is not installed. Creating a simple placeholder...")
    # Create a simple text file as fallback
    os.makedirs('static/images', exist_ok=True)
    with open('static/images/hidden_message.png', 'w') as f:
        f.write("This is a placeholder. In a real scenario, check image metadata or use steganography tools.")
    print("Placeholder created. Install Pillow (pip install Pillow) for a proper image.")
