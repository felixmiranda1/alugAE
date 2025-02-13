from django.test import TestCase, override_settings
from payments.models import Payment
from accounts.models import Tenant, Landlord
from properties.models import Unit
from rent.models import Contract
from payments.services.receipt_extractor import PixReceiptExtractor
from payments.services.data_structurer import ReceiptDataStructurer
from datetime import datetime

@override_settings(DATABASES={  # 🔹 FORÇA O USO DO BANCO DE DESENVOLVIMENTO
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'alugae',  # Banco de desenvolvimento já existente
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
})
class TestPaymentIntegration(TestCase):
    """
    Integration test to verify if the extracted data from a real PIX receipt
    correctly matches the system records.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up test data in the development database.
        """
        super().setUpClass()  # 🔹 Usa `setUpClass` para evitar criação automática de BD de teste

        # 🔹 Dados extraídos de um comprovante real
        cls.tenant = Tenant.objects.create(
            user_id=1,  
            cpf="67782366234",  
            marital_status="Single",
            profession="Engineer",
            adoption_code="ABC123"
        )

        cls.landlord = Landlord.objects.create(
            user_id=2,  
            marital_status="Married",
            profession="Investor",
            pix_key="felix.miranda1@outlook.com"  # ID da Transação como identificador
        )

        cls.unit = Unit.objects.create(
            landlord=cls.landlord,
            property_id=1,  
            number="101"
        )

        cls.contract = Contract.objects.create(
            tenant=cls.tenant,
            landlord=cls.landlord,
            unit=cls.unit,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2025, 1, 1),
            rent_amount=1.00  # Valor real do comprovante
        )

    def test_payment_validation(self):
        """
        Tests if the extracted receipt data matches the expected tenant and landlord.
        """
        # 📄 Caminho do comprovante real
        receipt_path = "/Users/felixmiranda/alugAE/comprovante1.jpeg"

        # 🔍 Extração de texto do comprovante
        extracted_text = PixReceiptExtractor.process_receipt(receipt_path)

        # 📊 Estruturar os dados extraídos
        structured_data = ReceiptDataStructurer.structure_data(extracted_text)

        # ✅ Validar os dados extraídos contra os dados no banco
        self.assertEqual(structured_data["payer_name"], "Gabriella Salomão de Paula")
        self.assertEqual(structured_data["receiver_name"], "Felix Oliveira Miranda")
        self.assertEqual(float(structured_data["amount"]), self.contract.rent_amount)
        self.assertEqual(structured_data["transaction_id"], self.landlord.pix_key)

        print("\n✅ Payment validation test passed!")
