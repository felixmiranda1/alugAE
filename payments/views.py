import os
import uuid
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from payments.models import Payment
from payments.tasks import send_proof_received_confirmation_task
from payments.services.payment_processor import PaymentProcessor
from payments.services.receipt_extractor import PixReceiptExtractor
from payments.services.data_structurer import ReceiptDataStructurer
from django.db.models import Value, F
from django.db.models.functions import Concat
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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

def upload_receipt_form_public(request, payment_id=None, upload_token=None):
    """
    View para testar upload de comprovantes diretamente via formulário.
    Atualiza um payment existente com as informações extraídas do comprovante.
    """
    if request.method == "GET":
        # Garante que payment seja buscado na entrada do método GET
        payment = get_object_or_404(Payment, id=payment_id, upload_token=upload_token)

        return render(request, "payments/upload_receipt_public.html", {
            "payment_id": payment_id,
            "upload_token": upload_token,
            "landlord_name": payment.landlord.user.first_name,
            "amount_due": payment.amount_due,
            "due_date": payment.payment_due_date.strftime("%d/%m/%Y"),
        })

    elif request.method == "POST" and request.FILES.get("receipt"):
        receipt_file = request.FILES["receipt"]

        file_ext = os.path.splitext(receipt_file.name)[1].lower()
        file_path = f"/tmp/{uuid.uuid4()}{file_ext}"
        with open(file_path, "wb+") as destination:
            for chunk in receipt_file.chunks():
                destination.write(chunk)

        try:
            extracted_text = PixReceiptExtractor.process_receipt(file_path)
            print("📝 Texto extraído no upload_receipt_form:", extracted_text)

            structured_data = ReceiptDataStructurer.structure_data(extracted_text)
            print("📊 Dados estruturados no upload_receipt_form:", structured_data)

            if not structured_data or 'error' in structured_data:
                print("❌ Structured data is invalid or empty.")
                return JsonResponse({"error": "Structured data is invalid or empty."}, status=400)

            # Agora, delega para o PaymentProcessor, passando o payment_id e token diretamente
            payment = PaymentProcessor.process_and_store_payment(
                extracted_data=structured_data,
                payment_id=payment_id,
                token=upload_token,
                extracted_text=extracted_text
            )

            # Dispara task de confirmação
            send_proof_received_confirmation_task.delay(payment.tenant.id)

            return JsonResponse({
                "message": "Comprovante enviado e aguardando análise!",
                "payment_id": payment.id
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def upload_receipt_form_landlord(request):
    if request.method == 'POST':
        # Aqui fica o processamento do arquivo enviado via painel landlord
        # Exemplo:
        receipt_file = request.FILES.get('receipt')

        # ⚠️ Aqui você decide como processar: 
        # se cria um novo Payment ou atualiza algum existente
        # Exemplo (apenas ilustrativo):
        # payment = Payment.objects.create(...)

        return JsonResponse({'message': 'Comprovante enviado com sucesso!'})

    # GET → Renderiza o formulário para landlord
    context = {
        # Qualquer informação extra que queira passar pro template
    }

    return render(request, 'payments/upload_receipt_landlord.html', context)