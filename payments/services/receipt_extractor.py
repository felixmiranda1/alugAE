import os
import cv2
import pytesseract
from PIL import Image
import numpy as np

# Set the Tesseract path and TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/share/tessdata'
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

class PixReceiptExtractor:
    """
    Extracts relevant data from PIX payment receipts in image format.
    """

    @staticmethod
    def preprocess_image(image_path, target_width=800):
        """
        Pre-processes the image: resizes, converts to grayscale, and applies binarization.
        
        :param image_path: Path to the receipt image.
        :param target_width: Minimum width for upscaling.
        :return: Processed image for OCR.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Resize if the image width is too small
        h, w = image.shape[:2]
        if w < target_width:
            scale = target_width / w
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Otsu's binarization for better contrast
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary

    @staticmethod
    def extract_text_from_image(image_path):
        """
        Runs OCR on the pre-processed image to extract text.
        
        :param image_path: Path to the receipt image.
        :return: Extracted text.
        """
        processed_image = PixReceiptExtractor.preprocess_image(image_path)
        
        # Convert OpenCV image to PIL format for better compatibility
        pil_image = Image.fromarray(processed_image)

        # OCR Configurations: 
        # --oem 3 (LSTM model), --psm 6 (Assumes a single block of text)
        config = '--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(pil_image, lang='por', config=config)

        return extracted_text.strip()

    @staticmethod
    def process_receipt(image_path):
        """
        Main function to process the receipt and extract information.

        :param image_path: Path to the receipt image.
        :return: Extracted text from OCR.
        """
        print(f"🔍 Processing receipt: {image_path}")
        extracted_text = PixReceiptExtractor.extract_text_from_image(image_path)
        print(f"\n📝 Extracted Text:\n{extracted_text}\n")
        
        return extracted_text
