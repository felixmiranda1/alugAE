from django.db import models
from accounts.models import Tenant, Landlord
from properties.models import Unit
from rent.models import Contract

class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="payments")
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name="payments")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="payments")
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="payments")
    
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)  # Valor do pagamento
    transaction_id = models.CharField(max_length=35, unique=True)  # ID único da transação PIX
    payer_name = models.CharField(max_length=255)  # Nome do pagador no comprovante
    receiver_name = models.CharField(max_length=255)  # Nome do beneficiário no comprovante
    receiver_pix_key = models.CharField(max_length=255)  # Chave PIX do landlord
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_due_date = models.DateField(null=True, blank=True)  # Ou ajuste conforme regras
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('proof_received', 'Comprovante Recebido'),
        ('under_analysis', 'Em Análise'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('overdue', 'Vencido'),
        ('paid', 'Pago'),
        ('cancelled', 'Cancelado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    validation_notes = models.TextField(blank=True, null=True)  # Observações da validação
    extracted_text = models.TextField(blank=True, null=True)  # Raw extracted text from receipt
    upload_token = models.CharField(max_length=255, unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Data de registro do pagamento

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"

    class Meta:
        db_table = "payment"
