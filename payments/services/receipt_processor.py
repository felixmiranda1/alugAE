import os
from payments.services.receipt_extractor import PixReceiptExtractor
from payments.services.pdf_extractor import PDFReceiptExtractor

class ReceiptProcessor:
    """
    Centralized receipt processing service.
    Determines the file type and applies the correct extraction method.
    """

    @staticmethod
    def process_receipt(file_path):
        """
        Determines the file type and extracts text accordingly.

        :param file_path: Path to the receipt file (JPEG, PNG, PDF).
        :return: Extracted text.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Identify the file type
        file_extension = file_path.lower().split(".")[-1]

        if file_extension in ["jpg", "jpeg", "png"]:
            print(f"🖼 Processing image receipt: {file_path}")
            return PixReceiptExtractor.process_receipt(file_path)

        elif file_extension == "pdf":
            print(f"📄 Processing PDF receipt: {file_path}")
            return PDFReceiptExtractor.extract_text_from_pdf(file_path)

        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

