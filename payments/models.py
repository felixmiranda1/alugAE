from django.db import models
from accounts.models import Tenant, Landlord
from properties.models import Unit
from rent.models import Contract

class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="payments")
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name="payments")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="payments")
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="payments")
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Valor do pagamento
    transaction_id = models.CharField(max_length=35, unique=True)  # ID único da transação PIX
    payer_name = models.CharField(max_length=255)  # Nome do pagador no comprovante
    receiver_name = models.CharField(max_length=255)  # Nome do beneficiário no comprovante
    receiver_pix_key = models.CharField(max_length=255)  # Chave PIX do landlord
    payment_date = models.DateTimeField()  # Data e hora da transação
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('under_review', 'Em Análise'),
        ('rejected', 'Rejeitado')
    ]
    payment_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='under_review')
    validation_notes = models.TextField(blank=True, null=True)  # Observações da validação
    extracted_text = models.TextField(blank=True, null=True)  # Raw extracted text from receipt
    created_at = models.DateTimeField(auto_now_add=True)  # Data de registro do pagamento

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.payment_status}"

    class Meta:
        db_table = "payment"
