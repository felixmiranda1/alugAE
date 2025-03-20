import os
import logging
from payments.services.receipt_extractor import PixReceiptExtractor
from payments.services.pdf_extractor import PDFReceiptExtractor

IMAGE_EXTENSIONS = (".jpeg", ".png", ".jpg", ".tiff", ".bmp", ".webp")
logger = logging.getLogger(__name__)

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
        print(f"🔍 Verificando existência do arquivo: {file_path}")
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"✅ Arquivo encontrado: {file_path}")
        file_extension = os.path.splitext(file_path)[1].lower()
        print(f"File extension detected: {file_extension}")
        try:
            if file_extension in IMAGE_EXTENSIONS:
                print(f"🖼 Iniciando processamento de imagem: {file_path}")
                logger.info(f"🖼 Processing image receipt: {file_path}")
                return PixReceiptExtractor.process_receipt(file_path)

            elif file_extension == ".pdf":
                print(f"📄 Iniciando processamento de PDF: {file_path}")
                logger.info(f"📄 Processing PDF receipt: {file_path}")
                return PDFReceiptExtractor.extract_text_from_pdf(file_path)

            else:
                print(f"❌ Formato de arquivo não suportado: {file_extension}")
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            logger.error(f"❌ Error processing receipt: {e}")
            raise