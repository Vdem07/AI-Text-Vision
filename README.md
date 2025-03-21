# AI-Text-Vision
AI-Text-Vision is an application for text recognition in images using OCR (Optical Character Recognition) and ATR (Artificial Text Recognition) technologies. It supports two recognition methods:
1. Pytesseract (OCR) — a traditional optical text recognition method.
2. EasyOCR (ATR) — an AI-based method providing more accurate recognition of complex texts.
The program allows users to upload images, recognize text, edit it, copy it to the clipboard, and save it as .txt or .docx files.

# Features
1. Upload images (JPEG, PNG).
2. Drag-and-drop support for images.
3. Choose between OCR or ATR recognition methods.
4. Display recognized text.
5. Copy text to clipboard.
6. Save results as .txt or .docx.
7. Clear input fields.
8. Supports both English and Russian languages.

# Installation & Usage
1. Clone the repository:
```
git clone https://github.com/yourusername/AI-Text-Vision.git
cd AI-Text-Vision
```
2. Install Tesseract OCR:
For Pytesseract to work, install Tesseract OCR. Download and install it from [here](https://sourceforge.net/projects/tesseract-ocr.mirror/).
Then specify the path to the executable in the code:
```
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
```
3. Run the application:
```
python AI_Text_Vision.py
```
# How to Use
1. Select a recognition method (OCR or ATR).
2. Click "Open Image" or drag and drop an image into the upload area.
3. Wait for the recognition process to complete.
4. Copy or save the result as .txt or .docx.

# ScreenShots
![image](https://github.com/user-attachments/assets/f188cc93-5c84-426b-9cac-363eda1c3add)
![image](https://github.com/user-attachments/assets/745a5aa9-ef40-4bec-867d-1caefff54f2e)


# Dependencies
1. Python 3.8+
2. PyQt5
3. pytesseract
4. PIL (Pillow)
5. OpenCV (cv2)
6. easyocr
7. python-docx

Install them using:
```
pip install PyQt5 pytesseract pillow opencv-python easyocr python-docx
```

# License
This project is licensed under the MIT License.
