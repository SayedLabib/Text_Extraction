import pdfplumber
from PIL import Image
import pytesseract
import io
import tempfile
import os
import sys
from docx import Document
import numpy as np
import easyocr
from io import BytesIO
import zipfile
from googletrans import Translator
from app.core.config import settings

# Initialize EasyOCR reader with multiple languages
reader = easyocr.Reader(['en', 'es', 'fr', 'it'])  # Add more languages as needed

# Initialize translator coded by rafiun
translator = Translator()

async def translate_to_english(text):
    """Translates text to English if it's not in English."""
    try:
        if not text.strip():
            return text
            
        # Detect language
        detection = translator.detect(text[:100])  # Use first 100 chars for detection
        
        # If not English, translate to English
        if detection.lang != 'en':
            translated = translator.translate(text, dest='en')
            return f"{translated.text}]"
        return text
    except Exception as e:
        return f"{text}\n\n[Translation error: {str(e)}]"

# Function to perform OCR using EasyOCR
async def perform_ocr_with_easyocr(image):
    """Use EasyOCR to extract text from an image."""
    try:
        # Convert the image to a numpy array
        image_np = np.array(image)
        
        # Use EasyOCR to extract text
        result = reader.readtext(image_np)
        
        # Join the extracted text
        extracted_text = "\n".join([text[1] for text in result])
        return extracted_text
    except Exception as e:
        return f"OCR Error: {str(e)}"

#########################################################################
###############Ocr for extract data from pdf#############################
#########################################################################

async def extract_text_from_pdf(file_content):
    extracted_text = ""
    
    # Create a temporary file to work with pdfplumber
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name
    
    try:
        # Open the PDF with pdfplumber
        with pdfplumber.open(temp_path) as pdf:
            # Iterate through each page in the PDF
            for i, page in enumerate(pdf.pages):
                # Extract text using pdfplumber
                page_text = page.extract_text() or ""  # Handle None return
                
                # If no text is found, use OCR with EasyOCR
                if not page_text.strip():  # If no text is found
                    pil_image = page.to_image().to_pil()  # Convert the page to a PIL image
                    page_text = await perform_ocr_with_easyocr(pil_image)  # Perform OCR on the image
                
                # Translate non-English text to English
                page_text = await translate_to_english(page_text)
                
                extracted_text += f"Page {i+1}:\n{page_text}\n\n"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return extracted_text


#########################################################################
###############Ocr for extract data from image###########################
#########################################################################

async def extract_text_from_image(file_content):
    try:
        # Open the image using PIL
        image = Image.open(io.BytesIO(file_content))
        
        # Use EasyOCR to extract text
        extracted_text = await perform_ocr_with_easyocr(image)
        
        # Translate non-English text to English
        translated_text = await translate_to_english(extracted_text)
        return translated_text
    except Exception as e:
        return f"ERROR: {str(e)}"


#########################################################################
###############Ocr for extract data from docx############################
#########################################################################

async def extract_text_from_docx(file_content):
    extracted_text = ""

    # Create a temporary file to work with the DOCX
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name
    
    try:
        doc = Document(temp_path)

        # Extract text from paragraphs
        for para in doc.paragraphs:
            extracted_text += para.text + "\n"
        
        # Now handle any images in the DOCX file and use OCR on them
        # Extract images from the DOCX file
        with zipfile.ZipFile(temp_path, 'r') as docx_zip:
            image_files = [file for file in docx_zip.namelist() if file.startswith('word/media/')]

            for image_file in image_files:
                img_data = docx_zip.read(image_file)
                image = Image.open(BytesIO(img_data))

                # Perform OCR on the image using EasyOCR instead of Tesseract
                ocr_text = await perform_ocr_with_easyocr(image)
                extracted_text += f"\n[OCR Extracted from image {image_file}]:\n{ocr_text}\n"
        
        # Translate non-English text to English
        extracted_text = await translate_to_english(extracted_text)
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                # If we still can't delete it, let's just log and continue
                print(f"Warning: Could not delete temporary file {temp_path}")
            
    return extracted_text
