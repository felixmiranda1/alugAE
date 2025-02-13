import logging
from payments.models import Payment
from accounts.models import Tenant, Landlord
from properties.models import Unit
from rent.models import Contract
from datetime import datetime

logger = logging.getLogger(__name__)

class PaymentProcessor:
    """
    Processes extracted payment data and saves it to the database.
    """

    @staticmethod
    def process_and_store_payment(file_path, extracted_data):
        """
        Processes and saves a payment, linking it to the correct Tenant, Landlord, and Contract.
        """
        print("🔍 Processando pagamento...")
        print(f"📄 Dados extraídos recebidos: {extracted_data}")

        try:
            # 🔹 Identificar o Landlord pelo nome do recebedor
            landlord = Landlord.objects.get(user__first_name__icontains=extracted_data["receiver_name"].split()[0])
            print(f"✅ Landlord encontrado: {landlord}")

            # 🔹 Identificar o Tenant pelo nome do pagador
            tenant = Tenant.objects.get(user__first_name__icontains=extracted_data["payer_name"].split()[0])
            print(f"✅ Tenant encontrado: {tenant}")

            # 🔹 Identificar a Unit do Tenant
            unit = Unit.objects.get(tenant=tenant)
            print(f"✅ Unidade encontrada: {unit}")

            print(f"🆔 Tenant ID buscado: {tenant.id} (Banco: 10)")
            print(f"🆔 Landlord ID buscado: {landlord.id} (Banco: 2)")
            print(f"🆔 Unit ID buscado: {unit.id} (Banco: 8)")

            contract = Contract.objects.get(
                tenant_id=tenant.id,
                landlord_id=landlord.id,
                unit_id=unit.id,
                status="active"
            )

            print(f"✅ Contrato encontrado: {contract}")

            # 🔹 Criar o registro do pagamento no banco de dados
            print("💾 Criando pagamento no banco de dados...")
            payment = Payment.objects.create(
                tenant=tenant,
                landlord=landlord,
                unit=unit,
                contract=contract,
                amount=float(extracted_data["amount"]),
                transaction_id=extracted_data.get("transaction_id", "UNKNOWN"),
                payer_name=extracted_data["payer_name"],
                receiver_name=extracted_data["receiver_name"],
                receiver_pix_key=extracted_data.get("receiver_pix_key", "UNKNOWN"),
                payment_date=datetime.strptime(extracted_data["payment_date"], "%Y-%m-%dT%H:%M:%S"),
                payment_status="pending",
                created_at=datetime.now(),
            )

            print(f"✅ Pagamento salvo com sucesso! ID: {payment.id}")
            return payment

        except Tenant.DoesNotExist:
            print("❌ Tenant não encontrado!")
            raise ValueError("Tenant not found for payer name")

        except Landlord.DoesNotExist:
            print("❌ Landlord não encontrado!")
            raise ValueError("Landlord not found for receiver name")

        except Unit.DoesNotExist:
            print("❌ Unidade não encontrada!")
            raise ValueError("Unit not found for tenant")

        except Contract.DoesNotExist:
            print("❌ Nenhum contrato ativo encontrado!")
            raise ValueError("No active contract found for this Tenant and Landlord")

        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            raise e
