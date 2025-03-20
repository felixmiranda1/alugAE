from celery import shared_task
from django.utils import timezone
from payments.services.twilio_service import send_template_whatsapp_message
from accounts.models import Tenant
from rent.models import Contract
from django.conf import settings
import logging
from django.utils.crypto import get_random_string 
from payments.utils import generate_upload_link
from payments.models import Payment

logger = logging.getLogger(__name__)

@shared_task
def send_rent_payment_reminder_task(tenant_id, content_sid):
    """
    Celery task to send a rent payment reminder to a tenant via WhatsApp.

    Args:
        tenant_id (int): ID of the tenant in the database.
        content_sid (str): Template SID for the WhatsApp message.
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        phone_number = tenant.user.phone

        contract = Contract.objects.filter(tenant=tenant, status='active').first()

        if not contract:
            logger.warning(f"Nenhum contrato ativo encontrado para o tenant {tenant_id}")
            return

        payment = Payment.objects.filter(contract=contract, status='pending').latest('payment_due_date')

        if not payment:
            logger.warning(f"Nenhum payment encontrado para o tenant {tenant_id}")
            return

        link_upload = generate_upload_link(payment)

        variables_dict = {
            "1": tenant.user.first_name,
            "2": str(contract.rent_value),
            "3": payment.payment_due_date.strftime('%d/%m/%Y'),
            "4": link_upload
        }

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

    except Payment.DoesNotExist:
        logger.error(f"No payment found for tenant {tenant_id}.")

@shared_task
def send_payment_reminders():
    """
    Task to send payment reminders to tenants based on rent contract due dates.
    """
    today = timezone.now().date()

    # Busca contratos ativos na tabela alugae.rent_contract
    contracts = Contract.objects.filter(status='active')

    for contract in contracts:
        due_date = contract.payment_due_date

        # Adiciona ano/mês para o vencimento atual
        this_month_due = due_date.replace(month=today.month, year=today.year)

        delta_days = (this_month_due - today).days

        tenant = contract.tenant
        phone_number = tenant.user.phone

        payment = Payment.objects.filter(contract=contract, payment_due_date=this_month_due, status='pending').first()

        if not payment:
            logger.warning(f"Nenhum payment encontrado para o contrato {contract.id} na data {this_month_due}")
            continue

        link_upload = generate_upload_link(payment)

        variables_dict = {
            "1": tenant.user.first_name,
            "2": str(contract.rent_value),
            "3": this_month_due.strftime("%d/%m/%Y"),
            "4": link_upload
        }

        # 3 dias antes do vencimento
        if delta_days == 3:
            logger.info(f"Enviando lembrete de 3 dias antes para {tenant.user.email}")
            send_template_whatsapp_message(
                to_number=phone_number,
                content_sid=settings.TWILIO_TEMPLATE_PAYMENT_REMINDER_3DAYS,
                variables_dict=variables_dict
            )

        # No dia do vencimento
        elif delta_days == 0:
            logger.info(f"Enviando lembrete no dia do vencimento para {tenant.user.email}")
            send_template_whatsapp_message(
                to_number=phone_number,
                content_sid=settings.TWILIO_TEMPLATE_PAYMENT_REMINDER_DUEDATE,
                variables_dict=variables_dict
            )

        # 1 dia após o vencimento
        elif delta_days == -1:
            logger.info(f"Enviando lembrete de atraso para {tenant.user.email}")
            send_template_whatsapp_message(
                to_number=phone_number,
                content_sid=settings.TWILIO_TEMPLATE_PAYMENT_REMINDER_1DAY,
                variables_dict=variables_dict
            )

@shared_task
def send_proof_received_confirmation_task(tenant_id):
    """
    Sends a WhatsApp message to confirm the receipt of a payment proof.
    
    Args:
        tenant_id (int): ID of the tenant who sent the proof.
    """
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
def send_payment_status_notification_task(tenant_id, status, reason=None):
    """
    Sends a WhatsApp message to notify the tenant if the payment was approved or rejected.

    Args:
        tenant_id (int): ID of the tenant.
        status (str): Either 'approved' or 'rejected'.
        reason (str): Reason for rejection (optional).
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        phone_number = tenant.user.phone

        # Busca o último payment proof_received ou pending
        payment = Payment.objects.filter(tenant=tenant, status__in=['proof_received', 'pending']).latest('payment_due_date')

        if status == 'approved':
            content_sid = settings.TWILIO_TEMPLATE_APPROVED
            variables_dict = {
                "1": tenant.user.first_name,
                "2": str(payment.amount_due)
            }
            logger.info(f"Enviando notificação de pagamento APROVADO para {tenant.user.email}")

        elif status == 'rejected':
            content_sid = settings.TWILIO_TEMPLATE_REJECTED
            link_upload = generate_upload_link(payment)
            variables_dict = {
                "1": tenant.user.first_name,
                "2": reason,
                "3": link_upload
            }
            logger.info(f"Enviando notificação de pagamento REJEITADO para {tenant.user.email}")

        else:
            logger.warning(f"Status inválido '{status}' informado para tenant {tenant_id}")
            return

        sid = send_template_whatsapp_message(
            to_number=phone_number,
            content_sid=content_sid,
            variables_dict=variables_dict
        )

        if sid:
            logger.info(f"Notificação '{status}' enviada ao tenant {tenant_id}. Message SID: {sid}")
        else:
            logger.warning(f"Falha ao enviar notificação '{status}' ao tenant {tenant_id}")

    except Tenant.DoesNotExist:
        logger.error(f"Tenant com ID {tenant_id} não encontrado.")

    except Payment.DoesNotExist:
        logger.error(f"Payment não encontrado para tenant {tenant_id} para status '{status}'.")

@shared_task
def generate_payments():
    """
    Generates payments (invoices) for each active RentContract.
    Should run once a month (e.g., every 25th).
    """
    from payments.models import Payment
    from django.utils import timezone

    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    contracts = Contract.objects.filter(status='active')

    for contract in contracts:
        # Define a data de vencimento para o ciclo atual
        due_day = contract.payment_due_date
        due_date = timezone.datetime(year=current_year, month=current_month, day=due_day).date()

        # Evita duplicar payments no mesmo mês para o contrato
        exists = Payment.objects.filter(contract=contract, payment_due_date=due_date).exists()
        if exists:
            continue  # Já existe, não cria outro

        # Cria o novo payment (invoice)
        token = get_random_string(32)
        Payment.objects.create(
            contract=contract,
            tenant=contract.tenant,
            landlord=contract.landlord,
            unit=contract.unit,
            amount_due=contract.rent_value,
            payment_due_date=due_date,
            upload_token=token,
            status='pending'
        )

        logger.info(f"Payment created for contract {contract.id} with due date {due_date} and token {token}")
        print(f"Generated token for payment: {token}")