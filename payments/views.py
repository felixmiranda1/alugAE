import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .services.payment_processor import PaymentProcessor

class UploadReceiptView(APIView):
    """
    API endpoint to upload and process payment receipts (JPEG, PNG, PDF).
    """
    parser_classes = (MultiPartParser, FormParser)  # Allows file uploads

    def post(self, request, format=None):
        file = request.FILES.get("receipt")  # Get the uploaded file

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the file temporarily for processing
        temp_file_path = f"/tmp/{file.name}"

        with open(temp_file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            # Process the uploaded receipt
            payment = PaymentProcessor.process_and_store_payment(
                file_path=temp_file_path,
                tenant_id=request.data.get("tenant_id"),
                landlord_id=request.data.get("landlord_id"),
                unit_id=request.data.get("unit_id"),
                contract_id=request.data.get("contract_id")
            )

            return Response(
                {
                    "message": "Receipt processed successfully",
                    "payment_id": payment.id,
                    "transaction_id": payment.transaction_id,
                    "amount": payment.amount,
                    "status": payment.payment_status
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            # Remove temporary file after processing
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

def upload_receipt_form(request):
    """
    Renderiza o formulário de upload de comprovantes PIX.
    """
    return render(request, "payments/upload_receipt.html")