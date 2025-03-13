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
    def process_and_store_payment(extracted_data):
        """
        Processes and saves a payment, linking it to the correct Tenant, Landlord, and Contract.
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
            print("💾 Criando pagamento no banco de dados...")
            payment_status = "pending"

            # Example: if validation rules are met, we can mark it as paid (simple logic placeholder)
            if extracted_data.get("validation_passed", False):
                payment_status = "paid"

            print("🚀 Dados para criação do pagamento:")
            print(f"   Tenant ID: {tenant.id}")
            print(f"   Landlord ID: {landlord.id}")
            print(f"   Unit ID: {unit.id}")
            print(f"   Contract ID: {contract.id}")
            print(f"   Amount: {extracted_data['amount']}")
            print(f"   Transaction ID: {extracted_data.get('transaction_id', 'UNKNOWN')}")
            print(f"   Payment date: {extracted_data.get('payment_date')}")

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
                payment_date=parser.parse(extracted_data["payment_date"]),
                payment_status=payment_status,
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
