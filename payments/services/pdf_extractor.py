import pdfplumber
import pytesseract
import os
import cv2
from PIL import Image
import numpy as np

# Set the Tesseract path and TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/share/tessdata'
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

class PDFReceiptExtractor:
    """
    Extracts text from PIX payment receipts in PDF format.
    """

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """
        Extracts text from a PDF file. If the PDF is text-based, it uses pdfplumber.
        If it's an image-based PDF, it converts the first page to an image and applies OCR.
        
        :param pdf_path: Path to the receipt PDF file.
        :return: Extracted text.
        """
        text = ""

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text += extracted_text + "\n"

            if text.strip():  # If we successfully extracted text, return it
                return text.strip()

            else:  # If no text was found, treat the PDF as an image and apply OCR
                print("📄 No text detected in PDF. Using OCR on the first page...")

                # Convert the first page to an image
                image_path = PDFReceiptExtractor.convert_pdf_to_image(pdf_path)

                # Import PixReceiptExtractor **dentro da função** para evitar importação circular
                from payments.services.receipt_extractor import PixReceiptExtractor  
                
                # Use OCR on the extracted image
                return PixReceiptExtractor.process_receipt(image_path)

        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
            return None

    @staticmethod
    def convert_pdf_to_image(pdf_path):
        """
        Converts the first page of a PDF to an image for OCR processing.

        :param pdf_path: Path to the receipt PDF file.
        :return: Path to the generated image file.
        """
        try:
            import pdf2image

            images = pdf2image.convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
            image_path = pdf_path.replace(".pdf", ".jpeg")  # Save as JPEG
            images[0].save(image_path, "JPEG")

            print(f"📸 PDF converted to image: {image_path}")
            return image_path

        except Exception as e:
            print(f"❌ Error converting PDF to image: {e}")
            return None
