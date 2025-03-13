import os
import math
from PIL import Image, ImageDraw, ImageFont

def create_circular_icon(size, bg_color, fg_color, save_path):
    """Create a circular icon with the letter 'F' inside."""
    # Create a blank image with a transparent background
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw the circle
    margin = size // 10
    draw.ellipse([(margin, margin), (size - margin, size - margin)], fill=bg_color)
    
    # Try to load a font, or use the default
    try:
        font = ImageFont.truetype("arial.ttf", size // 2)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position to center it - use different methods depending on Pillow version
    try:
        # For newer Pillow versions
        bbox = draw.textbbox((0, 0), "F", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # For older Pillow versions
        try:
            text_width, text_height = draw.textsize("F", font=font)
        except:
            # Fallback for any version
            text_width, text_height = size // 3, size // 2
    
    position = ((size - text_width) // 2, (size - text_height) // 2 - size // 10)
    
    # Draw the text
    draw.text(position, "F", fill=fg_color, font=font)
    
    # Save the icon
    icon.save(save_path)
    print(f"Icon created: {save_path}")
    return icon

def create_logo(width, height, bg_color, fg_color, accent_color, save_path):
    """Create a logo for the fitness tracker app."""
    # Create a blank image with a transparent background
    logo = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    
    # Draw a rounded rectangle as background
    radius = height // 5
    draw.rectangle(
        [(radius, 0), (width - radius, height)],
        fill=bg_color
    )
    draw.rectangle(
        [(0, radius), (width, height - radius)],
        fill=bg_color
    )
    draw.ellipse([(0, 0), (radius * 2, radius * 2)], fill=bg_color)
    draw.ellipse([(width - radius * 2, 0), (width, radius * 2)], fill=bg_color)
    draw.ellipse([(0, height - radius * 2), (radius * 2, height)], fill=bg_color)
    draw.ellipse([(width - radius * 2, height - radius * 2), (width, height)], fill=bg_color)
    
    # Add "FITNESS" text
    try:
        font = ImageFont.truetype("arial.ttf", height // 3)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text dimensions based on Pillow version
    try:
        # For newer Pillow versions
        bbox = draw.textbbox((0, 0), "FITNESS", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # For older Pillow versions
        try:
            text_width, text_height = draw.textsize("FITNESS", font=font)
        except:
            # Fallback
            text_width, text_height = width // 2, height // 3
    
    # Draw "FITNESS"
    position = ((width - text_width) // 2, height // 6)
    draw.text(position, "FITNESS", fill=fg_color, font=font)
    
    # Calculate "TRACKER" text dimensions
    try:
        # For newer Pillow versions
        bbox = draw.textbbox((0, 0), "TRACKER", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # For older Pillow versions
        try:
            text_width, text_height = draw.textsize("TRACKER", font=font)
        except:
            # Fallback
            text_width, text_height = width // 2, height // 3
    
    # Draw "TRACKER"
    position = ((width - text_width) // 2, height // 2)
    draw.text(position, "TRACKER", fill=accent_color, font=font)
    
    # Save the logo
    logo.save(save_path)
    print(f"Logo created: {save_path}")
    return logo

def setup_assets():
    """Create assets directory and generate icon and logo."""
    # Get the assets directory path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    assets_dir = os.path.join(parent_dir, 'assets')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created assets directory at {assets_dir}")
    
    # Create the icon
    icon_path = os.path.join(assets_dir, 'icon.png')
    if not os.path.exists(icon_path):
        create_circular_icon(
            size=256, 
            bg_color="#2196F3",  # Blue
            fg_color="#FFFFFF",  # White
            save_path=icon_path
        )
    
    # Create the logo
    logo_path = os.path.join(assets_dir, 'logo.png')
    if not os.path.exists(logo_path):
        create_logo(
            width=400,
            height=150,
            bg_color="#2196F3",  # Blue
            fg_color="#FFFFFF",  # White
            accent_color="#FF4081",  # Pink
            save_path=logo_path
        )
    
    return assets_dir

if __name__ == "__main__":
    setup_assets() 