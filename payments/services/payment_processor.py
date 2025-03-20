import logging
from payments.models import Payment
from accounts.models import Tenant, Landlord
from properties.models import Unit
from rent.models import Contract
from datetime import datetime
from dateutil import parser
import unicodedata  # já no início junto com os outros imports

def normalize_name(name):
    if not name:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', name)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
    return only_ascii.strip().lower()

logger = logging.getLogger(__name__)

class PaymentProcessor:
    """
    Processes extracted payment data and saves it to the database.
    """

    @staticmethod
    def process_and_store_payment(extracted_data, payment_id=None, token=None, extracted_text=None):
        """
        Processes and updates an existing payment based on the extracted data.
        If payment_id and token are provided, updates the corresponding payment.
        Otherwise, searches for a pending payment for the tenant and contract.
        """
        print("🔍 Processando pagamento...")
        print(f"📄 Dados extraídos recebidos: {extracted_data}")

        try:
            # 🔹 Identificar o Landlord pelo nome do recebedor
            landlord_name = extracted_data["receiver_name"].strip().lower()
            tenant_name = extracted_data["payer_name"].strip().lower()

            landlord_first_name = landlord_name.split()[0]
            landlord_last_name = landlord_name.split()[-1]

            landlord = Landlord.objects.filter(
                user__first_name__icontains=landlord_first_name,
                user__last_name__icontains=landlord_last_name
            ).first()
            print(f"🎯 Landlord buscado com nome '{landlord_name}': {landlord}")

            if not landlord:
                raise ValueError("Landlord not found for receiver name")

            # 🔹 Identificar o Tenant pelo nome do pagador usando full name normalization
            tenants = Tenant.objects.filter(landlord=landlord)

            tenant = None
            for t in tenants:
                full_name = f"{t.user.first_name} {t.user.last_name}"
                normalized_full_name = normalize_name(full_name)

                print(f"🔍 Comparando '{normalized_full_name}' com '{tenant_name}'")

                if normalized_full_name == tenant_name:
                    tenant = t
                    print(f"✅ Tenant encontrado: {tenant}")
                    break

            if not tenant:
                raise ValueError("Tenant not found for payer name")

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
            # Determine which payment to update
            if payment_id and token:
                payment = Payment.objects.get(id=payment_id, upload_token=token)
            else:
                payment = Payment.objects.filter(
                    tenant=tenant,
                    contract=contract,
                    status='pending'
                ).first()

            if not payment:
                raise ValueError("No pending payment found for this tenant and contract")
            transaction_id = extracted_data.get('transaction_id')
            if not transaction_id:
                raise ValueError("Transaction ID not found in extracted data")
            
            # Update the payment with the extracted data
            payment.payer_name = extracted_data.get('payer_name', '')
            payment.receiver_name = extracted_data.get('receiver_name', '')
            payment.transaction_id = transaction_id
            payment.payment_date = parser.parse(extracted_data.get('payment_date')) if extracted_data.get('payment_date') else None
            payment.extracted_text = extracted_text or ''
            payment.status = 'proof_received'
            payment.save()

            print(f"✅ Payment updated successfully! ID: {payment.id}")
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
