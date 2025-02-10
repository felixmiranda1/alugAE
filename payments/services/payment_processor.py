from payments.services.receipt_processor import ReceiptProcessor
from payments.services.data_structurer import ReceiptDataStructurer
from payments.models import Payment
from accounts.models import Tenant, Landlord
from properties.models import Unit
from rent.models import Contract

class PaymentProcessor:
    """
    Handles the full processing of a receipt, from extraction to database storage.
    """

    @staticmethod
    def process_and_store_payment(file_path, tenant_id, landlord_id, unit_id, contract_id):
        """
        Extracts text from a receipt, structures the data, and saves it in the Payment model.

        :param file_path: Path to the receipt file (JPEG, PNG, PDF)
        :param tenant_id: ID of the tenant making the payment
        :param landlord_id: ID of the landlord receiving the payment
        :param unit_id: ID of the rental unit
        :param contract_id: ID of the contract
        :return: Created Payment object
        """
        # Step 1: Extract text from the receipt
        extracted_text = ReceiptProcessor.process_receipt(file_path)

        if not extracted_text:
            raise ValueError("Failed to extract text from receipt.")

        # Step 2: Structure the extracted data
        structured_data = ReceiptDataStructurer.structure_data(extracted_text)

        # Step 3: Validate extracted data
        transaction_id = structured_data.get("transaction_id")
        amount = structured_data.get("amount")
        payer_name = structured_data.get("payer_name")
        receiver_name = structured_data.get("receiver_name")
        receiver_pix_key = structured_data.get("receiver_pix_key")
        payment_date = structured_data.get("payment_date")
        error_flag = structured_data.get("error")  # If there were issues in extraction

        # Step 4: Define payment status based on errors
        payment_status = "under_review" if error_flag else "pending"

        # Step 5: Create and store the payment record
        payment = Payment.objects.create(
            tenant_id=tenant_id,
            landlord_id=landlord_id,
            unit_id=unit_id,
            contract_id=contract_id,
            amount=amount if amount else 0.00,  # Default to 0.00 if no amount extracted
            transaction_id=transaction_id if transaction_id else "UNKNOWN",
            payer_name=payer_name if payer_name else "UNKNOWN",
            receiver_name=receiver_name if receiver_name else "UNKNOWN",
            receiver_pix_key=receiver_pix_key if receiver_pix_key else "UNKNOWN",
            payment_date=payment_date if payment_date else None,
            extracted_text=extracted_text,
            payment_status=payment_status,
            validation_notes=error_flag if error_flag else None
        )

        print(f"✅ Payment registered: {payment}")
        return payment
