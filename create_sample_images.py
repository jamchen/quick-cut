#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

# Create sample directory if it doesn't exist
os.makedirs('examples', exist_ok=True)

# Define colors for each slide
colors = [
    (255, 100, 100),  # Light red
    (100, 255, 100),  # Light green
    (100, 100, 255),  # Light blue
]

# Create a sample image for each slide
for i, color in enumerate(colors, 1):
    # Create a new 800x600 image with the specified color
    img = Image.new('RGB', (800, 600), color)
    draw = ImageDraw.Draw(img)
    
    # Try to get a font (fallback to default if necessary)
    try:
        # Try a few common system fonts
        for font_name in ["Arial", "Helvetica", "DejaVuSans", "FreeSans"]:
            try:
                font = ImageFont.truetype(font_name, 40)
                break
            except IOError:
                continue
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Add text to the image
    text = f"Sample Image {i}"
    
    # Check if the font has textlength method (Pillow >= 8.0.0)
    # Otherwise use getsize (older Pillow versions)
    try:
        text_width = draw.textlength(text, font=font)
    except AttributeError:
        try:
            text_width, _ = draw.textsize(text, font=font)
        except:
            text_width = 200  # Fallback value
    
    position = ((800 - text_width) // 2, 250)
    
    # Use text method with different signature based on Pillow version
    try:
        draw.text(position, text, font=font, fill=(0, 0, 0))
    except TypeError:
        # For newer Pillow versions
        draw.text(xy=position, text=text, font=font, fill=(0, 0, 0))
    
    # Save the image
    img.save(f'examples/{i}.jpg')
    print(f"Created examples/{i}.jpg")

print("Sample images created successfully!") 