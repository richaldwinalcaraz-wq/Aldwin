import base64
import os
import re
from pathlib import Path

html_file = r"c:\Users\user\OneDrive\Documents\DashBoard Project\nexashop-funnel.html"
images_dir = r"c:\Users\user\OneDrive\Documents\DashBoard Project\images"
output_file = r"c:\Users\user\OneDrive\Documents\DashBoard Project\nexashop-funnel-embedded.html"

# Read HTML
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find all image paths and convert to base64
def replace_img_src(match):
    img_path = match.group(1)
    if img_path.startswith('images/'):
        full_path = os.path.join(images_dir, img_path.replace('images/', ''))
        if os.path.exists(full_path):
            with open(full_path, 'rb') as img:
                img_data = base64.b64encode(img.read()).decode('utf-8')
            # Determine MIME type
            ext = os.path.splitext(full_path)[1].lower()
            mime_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'}
            mime_type = mime_map.get(ext, 'image/jpeg')
            return f'src="data:{mime_type};base64,{img_data}"'
    return match.group(0)

# Replace all image src attributes
html_content = re.sub(r'src="(images/[^"]+)"', replace_img_src, html_content)

# Write output
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"[OK] Embedded images. File: {output_file}")
print(f"[OK] Size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
