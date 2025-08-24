import os

photos_dir = "photos"
images = [f for f in os.listdir(photos_dir) if f.lower().endswith(".jpg")]
images.sort()

print('::: {style="display: grid;grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));grid-gap: 1em;"}')
for img in images:
    print(f"![]({photos_dir}/{img})")
print(":::")