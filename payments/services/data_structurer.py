import re
from datetime import datetime

class ReceiptDataStructurer:
    """
    Extracts and structures relevant information from extracted receipt text.
    """

    MONTHS = {
        "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04", "MAI": "05", "JUN": "06",
        "JUL": "07", "AGO": "08", "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
    }

    @staticmethod
    def parse_date_from_text(text):
        """
        Attempts to extract and standardize the date from a receipt text.
        Supports formats like "O9 FEV 2025 - 12:06:47" and converts to YYYY-MM-DDTHH:MM:SS.
        """
        date_match = re.search(r'(\d{1,2})\s*([A-Z]{3})\s*(\d{2,4}) - (\d{2}:\d{2}:\d{2})', text, re.IGNORECASE)

        if date_match:
            day, month_str, year, time = date_match.groups()
            month = ReceiptDataStructurer.MONTHS.get(month_str.upper(), "01")
            if len(year) == 2:
                year = f"20{year}"
            return f"{year}-{month}-{day.zfill(2)}T{time}"

        return None

    @staticmethod
    def structure_data(extracted_text):
        """
        Processes raw extracted text and structures the payment data.

        :param extracted_text: Raw text extracted from the receipt.
        :return: Dictionary with structured data (amount, transaction_id, payer_name, receiver_name, etc.)
        """
        if not extracted_text or not extracted_text.strip():
            return {"error": "No text extracted from receipt"}

        data = {}

        # 🔹 Extract `amount`
        amount_match = re.search(r'(?i)valor\s*R\$\s?(\d+(?:[.,]\d{2})?)', extracted_text)
        if amount_match:
            data["amount"] = amount_match.group(1).replace(",", ".")

        # 🔹 Extract `payer_name`
        payer_match = re.search(r'Origem\s*Nome\s+([^\n]+)', extracted_text)
        if payer_match:
            data["payer_name"] = payer_match.group(1).strip()

        # 🔹 Extract `receiver_name`
        receiver_match = re.search(r'Destino\s*Nome\s+([^\n]+)', extracted_text)
        if receiver_match:
            data["receiver_name"] = receiver_match.group(1).strip()

        # 🔹 Extract `receiver_pix_key` (Chave PIX do recebedor)
        pix_key_match = re.search(r'Chave Pix[:\s]+([\w@.-]+)', extracted_text, re.IGNORECASE)
        if pix_key_match:
            data["receiver_pix_key"] = pix_key_match.group(1).strip()

        # 🔹 Extract `transaction_id` (ID da transação)
        transaction_match = re.search(r'ID da transa[cç][aã]o:\s*([A-Za-z0-9]+)', extracted_text)
        if transaction_match:
            data["transaction_id"] = transaction_match.group(1).strip()

        # 🔹 Extract `payment_date`
        payment_date = ReceiptDataStructurer.parse_date_from_text(extracted_text)
        if payment_date:
            data["payment_date"] = payment_date

        return data
