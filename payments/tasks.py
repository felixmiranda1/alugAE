from celery import shared_task
from django.utils import timezone
from payments.services.twilio_service import send_template_whatsapp_message
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_rent_payment_reminder_task(tenant_id, content_sid, variables_dict):
    """
    Celery task to send a rent payment reminder to a tenant via WhatsApp.

    Args:
        tenant_id (int): ID of the tenant in the database.
        content_sid (str): Template SID for the WhatsApp message.
        variables_dict (dict): Variables for the template message.
    """
    from accounts.models import Tenant  # Import aqui para evitar circular import
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        phone_number = tenant.user.phone

        sid = send_template_whatsapp_message(
            to_number=phone_number,
            content_sid=content_sid,
            variables_dict=variables_dict
        )

        if sid:
            logger.info(f"Reminder sent to tenant {tenant_id}. Message SID: {sid}")
        else:
            logger.warning(f"Reminder to tenant {tenant_id} failed to send.")

    except Tenant.DoesNotExist:
        logger.error(f"Tenant with ID {tenant_id} does not exist.")


@shared_task
def send_payment_reminders():
    """
    Task to send payment reminders to tenants based on rent contract due dates.
    """
    from rent.models import RentContract
    from accounts.models import Tenant
    from django.conf import settings

    today = timezone.now().date()

    # Busca contratos ativos na tabela alugae.rent_contract
    contracts = RentContract.objects.filter(status='active')

    for contract in contracts:
        due_date = contract.payment_due_date

        # Adiciona ano/mês para o vencimento atual
        this_month_due = due_date.replace(month=today.month, year=today.year)

        delta_days = (this_month_due - today).days

        tenant = contract.tenant
        phone_number = tenant.user.phone

        # 3 dias antes do vencimento
        if delta_days == 3:
            logger.info(f"Enviando lembrete de 3 dias antes para {tenant.user.email}")
            send_template_whatsapp_message(
                to_number=phone_number,
                content_sid=settings.TWILIO_TEMPLATE_PAYMENT_REMINDER_3DAYS,
                variables_dict={
                    "1": this_month_due.strftime("%d/%m/%Y"),
                    "2": str(contract.rent_value),
                }
            )

        # No dia do vencimento
        elif delta_days == 0:
            logger.info(f"Enviando lembrete no dia do vencimento para {tenant.user.email}")
            send_template_whatsapp_message(
                to_number=phone_number,
                content_sid=settings.TWILIO_TEMPLATE_PAYMENT_REMINDER_DUEDATE,
                variables_dict={
                    "1": this_month_due.strftime("%d/%m/%Y"),
                    "2": str(contract.rent_value),
                }
            )

        # 1 dia após o vencimento
        elif delta_days == -1:
            logger.info(f"Enviando lembrete de atraso para {tenant.user.email}")
            send_template_whatsapp_message(
                to_number=phone_number,
                content_sid=settings.TWILIO_TEMPLATE_PAYMENT_REMINDER_1DAY,
                variables_dict={
                    "1": this_month_due.strftime("%d/%m/%Y"),
                    "2": str(contract.rent_value),
                }
            )

@shared_task
def send_proof_received_confirmation_task(tenant_id):
    """
    Sends a WhatsApp message to confirm the receipt of a payment proof.
    
    Args:
        tenant_id (int): ID of the tenant who sent the proof.
    """
    from accounts.models import Tenant
    from django.conf import settings

    try:
        tenant = Tenant.objects.get(id=tenant_id)
        phone_number = tenant.user.phone

        logger.info(f"Enviando confirmação de recebimento do comprovante para {tenant.user.email}")

        sid = send_template_whatsapp_message(
            to_number=phone_number,
            content_sid=settings.TWILIO_TEMPLATE_PROOF_RECEIVED,
            variables_dict={
                "1": tenant.user.first_name,  # Exemplo: nome do tenant para personalização
            }
        )

        if sid:
            logger.info(f"Confirmação enviada ao tenant {tenant_id}. Message SID: {sid}")
        else:
            logger.warning(f"Confirmação ao tenant {tenant_id} falhou no envio.")

    except Tenant.DoesNotExist:
        logger.error(f"Tenant with ID {tenant_id} does not exist.")
    
@shared_task
def send_payment_status_notification_task(tenant_id, status):
    """
    Sends a WhatsApp message to notify the tenant if the payment was approved or rejected.

    Args:
        tenant_id (int): ID of the tenant.
        status (str): Either 'approved' or 'rejected'.
    """
    from accounts.models import Tenant
    from django.conf import settings

    try:
        tenant = Tenant.objects.get(id=tenant_id)
        phone_number = tenant.user.phone

        if status == 'approved':
            content_sid = settings.TWILIO_TEMPLATE_APPROVED
            logger.info(f"Enviando notificação de pagamento APROVADO para {tenant.user.email}")
        elif status == 'rejected':
            content_sid = settings.TWILIO_TEMPLATE_REJECTED
            logger.info(f"Enviando notificação de pagamento REJEITADO para {tenant.user.email}")
        else:
            logger.warning(f"Status inválido '{status}' informado para tenant {tenant_id}")
            return

        sid = send_template_whatsapp_message(
            to_number=phone_number,
            content_sid=content_sid,
            variables_dict={
                "1": tenant.user.first_name,  # Personalização com nome
            }
        )

        if sid:
            logger.info(f"Notificação '{status}' enviada ao tenant {tenant_id}. Message SID: {sid}")
        else:
            logger.warning(f"Falha ao enviar notificação '{status}' ao tenant {tenant_id}")

    except Tenant.DoesNotExist:
        logger.error(f"Tenant com ID {tenant_id} não encontrado.")