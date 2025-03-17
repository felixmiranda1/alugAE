import re
from datetime import datetime
import unicodedata

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
    def normalize_text(text):
        """
        Normalizes text by removing accents and unwanted characters.
        """
        nfkd_form = unicodedata.normalize('NFKD', text)
        only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', only_ascii)
        return cleaned.strip()

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
        lines = extracted_text.splitlines()

        # 🔹 Extract `amount`
        amount_match = re.search(r'R\$\s?([\d\.]+,\d{2})', extracted_text)
        if amount_match:
            amount_str = amount_match.group(1).replace('.', '').replace(',', '.')
            data["amount"] = amount_str
            print(f"💰 Valor extraído: {data['amount']}")
        else:
            print("❌ Valor não encontrado!")

        # 🔹 Extract `payer_name`
        payer_match = re.search(r'(Origem|Quem pagou|Pagador)[\s\S]*?Nome[:\s]+([^\n]+)', extracted_text, re.IGNORECASE)
        if payer_match:
            data["payer_name"] = payer_match.group(2).strip()
            print(f"👤 Nome do pagador extraído: {data['payer_name']}")
        else:
            print("❌ Nome do pagador não encontrado!")

        # 🔹 Extract `receiver_name`
        receiver_match = re.search(r'(Destino|Quem recebeu|Benefici[aá]rio)[\s\S]*?Nome[:\s]+([^\n]+)', extracted_text, re.IGNORECASE)
        if receiver_match:
            data["receiver_name"] = receiver_match.group(2).strip()
            print(f"🏦 Nome do recebedor extraído: {data['receiver_name']}")
        else:
            print("❌ Nome do recebedor não encontrado!")

        # 🔹 Extract `receiver_pix_key` (Chave PIX do recebedor)
        pix_key_match = re.search(r'(Chave(?: Pix)?)[\s\S]*?[:\s]+([\w\d@.\-+]{8,})', extracted_text, re.IGNORECASE)
        if pix_key_match:
            data["receiver_pix_key"] = pix_key_match.group(2).strip()
            print(f"🔑 Chave PIX do recebedor extraída: {data['receiver_pix_key']}")
        else:
            print("❌ Chave PIX do recebedor não encontrada!")

        # 🔹 Extract `transaction_id` (ID da transação)
        data["transaction_id"] = None
        for idx, line in enumerate(lines):
            if "id da transacao" in line.lower() or "id da transação" in line.lower():
                if idx + 1 < len(lines):
                    raw_transaction_id = lines[idx + 1]
                    cleaned_transaction_id = ReceiptDataStructurer.normalize_text(raw_transaction_id)
                    if cleaned_transaction_id:
                        data["transaction_id"] = cleaned_transaction_id
                        print(f"🆔 ID da transação extraído: {data['transaction_id']}")
                break

        if not data["transaction_id"]:
            print("❌ ID da transação não encontrado!")

        # 🔹 Extract `payment_date`
        payment_date_match = re.search(
            r'Data do pagamento.*?(\d{2}/\d{2}/\d{4})',
            extracted_text,
            re.IGNORECASE
        )

        payment_date = payment_date_match.group(1) if payment_date_match else None
        if payment_date:
            data["payment_date"] = payment_date
            print(f"📅 Data do pagamento extraída: {data['payment_date']}")
        else:
            print("❌ Data do pagamento não encontrada!")

        return data
