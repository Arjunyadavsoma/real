
#client = Groq(api_key=os.environ.get("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"))

import os
from docx import Document
from PIL import Image
import pdfplumber
import pytesseract
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=api_key)
def summarize_text(text):
    """
    Summarizes the input text using the Groq API.
    
    Args:
        text (str): The text to be summarized.
        
    Returns:
        str: Summarized text or error message.
    """
    try:
        # Make an API call to summarize the text
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Summarize the following text: {text}",
            }],
            model="llama3-8b-8192"  # Customize with the desired model
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def extract_text_from_file(filepath):
    """
    Extracts text from a file based on its extension.

    Args:
        filepath (str): Path to the file to extract text from.
        
    Returns:
        str: Extracted text or error message.
    """
    if not os.path.exists(filepath):
        return "File does not exist."

    ext = filepath.split('.')[-1].lower()

    try:
        # Determine file type based on the extension and call appropriate extraction function
        if ext == 'pdf':
            return extract_text_from_pdf(filepath)
        elif ext == 'docx':
            return extract_text_from_docx(filepath)
        elif ext in ['jpg', 'jpeg', 'png']:
            return extract_text_from_image(filepath)
        else:
            return "Unsupported file type. Supported types: PDF, DOCX, JPG, JPEG, PNG."
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_text_from_pdf(filepath):
    """
    Extracts text from a PDF file.

    Args:
        filepath (str): Path to the PDF file.
        
    Returns:
        str: Extracted text or error message.
    """
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""  # Handle pages with no text
    except Exception as e:
        text = f"Error extracting text from PDF: {str(e)}"
    return text

def extract_text_from_docx(filepath):
    """
    Extracts text from a DOCX file.

    Args:
        filepath (str): Path to the DOCX file.
        
    Returns:
        str: Extracted text or error message.
    """
    text = ""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        text = f"Error extracting text from DOCX: {str(e)}"
    return text

def extract_text_from_image(filepath):
    """
    Extracts text from an image file using Tesseract OCR.

    Args:
        filepath (str): Path to the image file.
        
    Returns:
        str: Extracted text or error message.
    """
    try:
        image = Image.open(filepath)
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"
