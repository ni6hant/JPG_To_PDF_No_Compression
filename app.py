import img2pdf
import os

# Folder containing JPG files
input_folder = "images"

# Output PDF name
output_pdf = "combined.pdf"

# Get JPG files in sorted order
jpg_files = sorted([
    os.path.join(input_folder, f)
    for f in os.listdir(input_folder)
    if f.lower().endswith((".jpg", ".jpeg"))
])

# Create PDF without altering image data
with open(output_pdf, "wb") as f:
    f.write(img2pdf.convert(jpg_files))

print(f"Created: {output_pdf}")