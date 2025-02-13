import unittest
from datetime import datetime
from payments.services.data_structurer import ReceiptDataStructurer

class TestDataStructurer(unittest.TestCase):
    """
    Unit tests for the ReceiptDataStructurer.
    """

    def test_extract_correct_data(self):
        """
        Test if the structurer correctly extracts and formats the expected fields.
        """
        extracted_text = """
        Pagador: João da Silva
        Beneficiário: Empresa XYZ LTDA
        Chave Pix: empresa@xyz.com
        ID da Transação: E1234567890ABCDEF1234567890ABCDE
        Valor: R$ 850,00
        O9 FEV 2025 - 12:06:47
        """

        structured_data = ReceiptDataStructurer.structure_data(extracted_text)

        self.assertEqual(structured_data["amount"], "850.00")
        self.assertEqual(structured_data["transaction_id"], "E1234567890ABCDEF1234567890ABCDE")
        self.assertEqual(structured_data["payer_name"], "João da Silva")
        self.assertEqual(structured_data["receiver_name"], "Empresa XYZ LTDA")
        self.assertEqual(structured_data["receiver_pix_key"], "empresa@xyz.com")
        self.assertEqual(structured_data["payment_date"], datetime(2025, 2, 9, 12, 6, 47))

    def test_invalid_format_date(self):
        """
        Test if an invalid date format returns None.
        """
        extracted_text = "Data de pagamento: 99 XXX 2025 - 12:06:47"
        structured_data = ReceiptDataStructurer.structure_data(extracted_text)

        self.assertIn("error", structured_data)
        self.assertEqual(structured_data["error"], "Failed to extract payment date")

    def test_missing_fields(self):
        """
        Test if missing fields result in appropriate errors.
        """
        extracted_text = "Apenas um texto aleatório sem informações válidas."

        structured_data = ReceiptDataStructurer.structure_data(extracted_text)

        self.assertIn("error", structured_data)
        self.assertEqual(structured_data["error"], "No text extracted from receipt")

    def test_multiple_values_detected(self):
        """
        Test if the system detects multiple values and marks for manual review.
        """
        extracted_text = """
        Pagador: João da Silva
        Beneficiário: Empresa XYZ LTDA
        Chave Pix: empresa@xyz.com
        ID da Transação: E1234567890ABCDEF1234567890ABCDE
        Valor: R$ 850,00
        Valor: R$ 1.200,00
        O9 FEV 2025 - 12:06:47
        """

        structured_data = ReceiptDataStructurer.structure_data(extracted_text)

        self.assertIn("error", structured_data)
        self.assertEqual(structured_data["error"], "Multiple values detected, needs manual review")

if __name__ == "__main__":
    unittest.main()
