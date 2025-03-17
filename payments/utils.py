from django.conf import settings

def generate_upload_link(payment):
    """
    Gera o link completo para o tenant enviar o comprovante de pagamento.

    Args:
        payment (Payment): Instância do pagamento.

    Returns:
        str: URL completa no formato https://seusite.com/payments/upload/{payment_id}/{upload_token}/
    """
    return f"{settings.ALUGAE_BASE_URL}/payments/upload/{payment.id}/{payment.upload_token}/"