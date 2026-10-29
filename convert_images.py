import os
from PIL import Image

# Register AVIF plugin support if available
try:
    import pillow_avif
except ImportError:
    pass

# Supported source image extensions including WEBP and AVIF
valid_extensions = (
    '.jpg', '.jpeg', '.jfif', '.webp', '.avif', 
    '.PNG', '.JPG', '.WEBP', '.AVIF'
)

# Get current directory path where script lives
script_dir = os.path.dirname(os.path.abspath(__file__))

print("Converting images (.webp, .avif, .jpg, .jfif) to .png...\n")

converted_count = 0

for file_name in os.listdir(script_dir):
    name, ext = os.path.splitext(file_name)
    
    # Target files named 1, 2, 3... up to 30 that aren't already valid .png files
    if name.isdigit() and ext.lower() in valid_extensions and ext.lower() != '.png':
        old_path = os.path.join(script_dir, file_name)
        new_path = os.path.join(script_dir, f"{name}.png")
        
        try:
            with Image.open(old_path) as img:
                # Convert image to RGB mode and save as clean PNG
                img.convert('RGB').save(new_path, 'PNG')
            
            print(f" Converted: {file_name} -> {name}.png")
            converted_count += 1
            
            # Remove original file to keep project directory clean
            os.remove(old_path)
        except Exception as e:
            print(f" Error converting {file_name}: {e}")

print(f"\nFinished! Converted {converted_count} file(s) into proper .png images.")