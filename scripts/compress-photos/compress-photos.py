from PIL import Image
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(script_dir, "og-photos")
output_folder = os.path.join(script_dir, "photos_compressed")
os.makedirs(output_folder, exist_ok=True)

# Loop through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path)

        # Optional: Resize image (uncomment to use)
        # img = img.resize((img.width // 2, img.height // 2))

        # Save with reduced quality (for JPEG)
        output_path = os.path.join(output_folder, filename)
        if filename.lower().endswith(('.jpg', '.jpeg')):
            img.save(output_path, "JPEG", quality=60, optimize=True)
        else:  # For PNG
            img.save(output_path, "PNG", optimize=True)

        print(f"Compressed: {filename}")