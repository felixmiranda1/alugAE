import unittest
from payments.services.receipt_extractor import PixReceiptExtractor

# Caminhos de arquivos de teste (substitua pelos arquivos reais)
TEST_RECEIPTS = [
    "/Users/felixmiranda/alugAE/comprovante1.jpeg",
    "//Users/felixmiranda/alugAE/comprovante2.jpeg",
    "/Users/felixmiranda/alugAE/comprovante3.pdf",
    "/Users/felixmiranda/alugAE/comprovante4.jpeg"
]

class TestReceiptExtraction(unittest.TestCase):
    """
    Tests the text extraction from different formats of receipts.
    """

    def test_extract_text_from_images_and_pdfs(self):
        """
        Check if the text is correctly extracted from different receipt formats.
        """
        for file_path in TEST_RECEIPTS:
            with self.subTest(file=file_path):
                from payments.services.pdf_extractor import PDFReceiptExtractor  # Importação correta
                extracted_text = (
                        PixReceiptExtractor.extract_text_from_image(file_path)
                        if file_path.endswith((".jpeg", ".png"))
                        else PDFReceiptExtractor.extract_text_from_pdf(file_path)  # Agora chamamos a classe correta!
                    )
                print(f"\n🔍 Extracted Text from {file_path}:\n{extracted_text}\n")

                self.assertTrue(len(extracted_text) > 10, "Extracted text is too short or empty!")

if __name__ == "__main__":
    unittest.main()
