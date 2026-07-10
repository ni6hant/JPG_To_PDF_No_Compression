# ⚠️ AI Assistance Notice
This application was developed with substantial assistance from LLMs.
The implementation, structure, debugging, and code generation were AI-assisted.
Human decisions, feature selection, testing, and project direction were provided by the project creator.

1.0 and 1.1 Versions: ChatGPT.
1.2: Claude.

# JPG → PDF Combiner without compression

A lightweight Windows utility for combining multiple JPG/JPEG images into a single PDF while preserving the original image data whenever possible.

## Developer Notes

### How the application works

The application uses a simple pipeline:

1. Images are imported using either:

   * File selection
   * Drag-and-drop support

2. Imported images are stored internally as a list of file paths.

3. Users can reorder images:

   * Move up
   * Move down
   * Alphabetical sorting

4. A preview panel displays the currently selected image and automatically scales to the application window size.

5. During PDF creation:

   * Image files are passed directly into `img2pdf`
   * JPG data is embedded into the PDF without unnecessary recompression or quality reduction when possible
   * Image dimensions are preserved

### Main libraries used

* Python
* tkinter → graphical interface
* tkinterdnd2 → drag-and-drop support
* Pillow (PIL) → image previews and scaling
* img2pdf → PDF generation while preserving original image data
* PyInstaller → executable generation

### Output behavior

Default output location:

* Same folder as the executable

Default file naming:

combined_<first_image_name>.pdf

Example:

combined_photo001.pdf

### Packaging

Executable generated with PyInstaller:

pyinstaller --onefile --windowed --hidden-import=tkinterdnd2 --exclude-module matplotlib --exclude-module numpy --exclude-module pandas --exclude-module scipy jpg_to_pdf_gui.py

### Notes

This application intentionally avoids image processing during PDF generation. The goal is to preserve the original JPG image quality and avoid introducing unnecessary modifications.
