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
        Supports formats like "O9 FEV 2025 - 12:06:47" and converts to dd/mm/yyyy HH:MM:SS.
        """
        date_match = re.search(r'(\d{1,2})\s*([A-Z]{3})\s*(\d{2,4})', text, re.IGNORECASE)
        time_match = re.search(r'(\d{2}:\d{2}(:\d{2})?)', text)

        if date_match:
            day = date_match.group(1).zfill(2)  # Garante dois dígitos para o dia
            month_str = date_match.group(2).upper()
            year = date_match.group(3)

            month = ReceiptDataStructurer.MONTHS.get(month_str, "01")  # Converte mês para número

            # Ajusta ano se for fornecido com dois dígitos
            if len(year) == 2:
                year = f"20{year}"

            formatted_date = f"{day}/{month}/{year}"
        else:
            formatted_date = None

        formatted_time = time_match.group(1) if time_match else "00:00:00"

        if formatted_date:
            try:
                return datetime.strptime(f"{formatted_date} {formatted_time}", "%d/%m/%Y %H:%M:%S")
            except ValueError:
                return None  # Retorna None se a conversão falhar

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

        # Extract amount
        amount_match = re.search(r'(?i)R\$\s?(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})', extracted_text)
        if amount_match:
            data["amount"] = amount_match.group(1).replace(".", "").replace(",", ".")

        # Extract transaction ID
        transaction_match = re.search(r'\b(E[A-Za-z0-9]{31})\b', extracted_text)
        if transaction_match:
            data["transaction_id"] = transaction_match.group(1)

        # Extract payer name
        payer_match = re.search(r'(?i)(?:Pagador|De|Remetente)[:\s]+([^\n]+)', extracted_text)
        if payer_match:
            data["payer_name"] = payer_match.group(1).strip()

        # Extract receiver name
        receiver_match = re.search(r'(?i)(?:Beneficiário|Para|Recebedor)[:\s]+([^\n]+)', extracted_text)
        if receiver_match:
            data["receiver_name"] = receiver_match.group(1).strip()

        # Extract receiver PIX key
        pix_key_match = re.search(r'(?i)(?:Chave Pix|PIX)[:\s]+([^\n]+)', extracted_text)
        if pix_key_match:
            data["receiver_pix_key"] = pix_key_match.group(1).strip()

        # Extract payment date
        payment_date = ReceiptDataStructurer.parse_date_from_text(extracted_text)
        if payment_date:
            data["payment_date"] = payment_date
        else:
            data["error"] = "Failed to extract payment date"

        return data
