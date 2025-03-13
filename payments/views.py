import os
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from payments.services.payment_processor import PaymentProcessor
from payments.services.receipt_extractor import PixReceiptExtractor
from payments.services.data_structurer import ReceiptDataStructurer

class UploadReceiptView(APIView):
    """
    API endpoint to upload and process payment receipts.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        print("📥 Recebendo requisição de upload...")  # Verifica se a API foi chamada

        file = request.FILES.get("receipt")
        if not file:
            print("❌ Nenhum arquivo foi enviado!")
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        file_ext = os.path.splitext(file.name)[1].lower()
        temp_file_path = f"/tmp/{uuid.uuid4()}{file_ext}"
        with open(temp_file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        print("🖼 Arquivo salvo temporariamente:", temp_file_path)

        try:
            # 🔍 Extração do texto do comprovante
            extracted_text = PixReceiptExtractor.process_receipt(temp_file_path)
            print("📝 Texto extraído do comprovante:", extracted_text)

            # 📊 Estruturar os dados extraídos
            structured_data = ReceiptDataStructurer.structure_data(extracted_text)
            print("📊 Dados estruturados extraídos:", structured_data)
            print(f"❗ Tipo de structured_data: {type(structured_data)}")
            print(f"❗ Tamanho de structured_data: {len(structured_data)}")

            if not structured_data:
                print("❌ Structured data is empty! Não foi possível extrair informações do comprovante.")
                return Response({"error": "Structured data is empty"}, status=status.HTTP_400_BAD_REQUEST)

            # 💾 TESTE: Print antes de chamar o `PaymentProcessor`
            print("💾 Chamando PaymentProcessor...")

            # 💾 Processar e salvar o pagamento no banco
            payment = PaymentProcessor.process_and_store_payment(structured_data)
            print("✅ Pagamento processado com sucesso!")

            return Response(
                {
                    "message": "Receipt processed successfully",
                    "payment_id": payment.id,
                    "transaction_id": payment.transaction_id,
                    "amount": payment.amount,
                    "status": payment.payment_status,
                    "structured_data": structured_data,
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            import traceback
            print(f"❌ Erro inesperado: {e}")
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

def upload_receipt_form(request):
    """
    View para testar upload de comprovantes diretamente via formulário.
    Retorna o texto extraído e os dados estruturados para depuração.
    """
    if request.method == "GET":
        # 🔹 Se for uma requisição GET, renderiza o formulário HTML
        return render(request, "payments/upload_receipt.html")

    elif request.method == "POST" and request.FILES.get("receipt"):
        receipt_file = request.FILES["receipt"]

        # Salvar temporariamente o arquivo
        file_ext = os.path.splitext(receipt_file.name)[1].lower()
        file_path = f"/tmp/{uuid.uuid4()}{file_ext}"
        with open(file_path, "wb+") as destination:
            for chunk in receipt_file.chunks():
                destination.write(chunk)

        try:
            # 🔍 Extração do texto
            extracted_text = PixReceiptExtractor.process_receipt(file_path)
            print("📝 Texto extraído no upload_receipt_form:", extracted_text)

            # 📊 Estruturar os dados extraídos
            structured_data = ReceiptDataStructurer.structure_data(extracted_text)
            print("📊 Dados estruturados no upload_receipt_form:", structured_data)
            print(f"❗ Tipo de structured_data: {type(structured_data)}")
            print(f"❗ Tamanho de structured_data: {len(structured_data)}")
            if not structured_data or 'error' in structured_data:
                print("❌ Structured data is invalid or empty.")
            else:
                print("💾 Chamando PaymentProcessor no formulário...")
                payment = PaymentProcessor.process_and_store_payment(structured_data)
                print(f"✅ Pagamento criado no formulário! ID: {payment.id}")

            # 🔄 Retornar JSON com os dados e o texto extraído
            return JsonResponse(
                {
                    "message": "Receipt processed successfully",
                    "raw_text": extracted_text,  # 🔍 Agora mostramos o texto bruto extraído
                    "structured_data": structured_data,  # 📊 Mostramos os dados estruturados
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        finally:
            # Remover arquivo temporário após o processamento
            if os.path.exists(file_path):
                os.remove(file_path)

    return JsonResponse({"error": "Invalid request"}, status=400)
