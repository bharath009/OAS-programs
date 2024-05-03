PDF Processing Script

Requirements

To run this script, you need to have Python installed on your system. You also need to install the following Python packages:

- PyPDF2
- pytesseract
- requests
- Pillow
- pdf2image
- pyzbar

Installation

Windows

1. Install Python:
   - Download the latest version of Python from the official website: Python Downloads
   - Run the installer and follow the installation instructions.
2. Open Command Prompt:
   - Press Win + R to open the Run dialog.
   - Type cmd and press Enter.
3. Navigate to your project directory:
   cd path\to\your\project
4. Install required packages using pip:
   pip install -r requirements.txt

macOS

1. Install Homebrew:
   - Open Terminal.
   - Paste the following command and press Enter:
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   - Follow the installation instructions.
2. Install Python:
   - Type the following command in Terminal and press Enter:
     brew install python@3.12
3. Navigate to your project directory:
   cd path/to/your/project
4. Install required packages using pip:
   pip install -r requirements.txt

Usage

1. Place your PDF files in a directory.
2. Open Command Prompt (Windows) or Terminal (macOS).
3. Navigate to your project directory:
   cd path\to\your\project
4. Run the script:
   python oasscript.py
5. Follow the on-screen instructions to select the directory containing the PDF files.
6. The script will process each PDF file in the directory, extract information, and rename the files based on the extracted data.

Author

Bharath Seshavarapu
