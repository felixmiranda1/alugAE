from twilio.rest import Client
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)

def send_template_whatsapp_message(to_number, content_sid, variables_dict):
    """
    Sends a WhatsApp template message using Twilio API.

    Args:
        to_number (str): Phone number with country code (e.g., +559491636074)
        content_sid (str): The Twilio Content Template SID (e.g., HXb5b62575e6e4ff6129ad7c8efe1f983e)
        variables_dict (dict): Variables to replace in the template (e.g., {"1": "Felix", "2": "3pm"})

    Returns:
        str: The SID of the message if sent successfully, None otherwise.
    """
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    whatsapp_from = settings.TWILIO_WHATSAPP_NUMBER

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            from_=whatsapp_from,
            content_sid=content_sid,
            content_variables=json.dumps(variables_dict),
            to=f'whatsapp:{to_number}'
        )

        logger.info(f"Template message sent to {to_number}. SID: {message.sid}")
        return message.sid

    except Exception as e:
        logger.error(f"Failed to send template message to {to_number}: {e}")
        return None