import resend
import os
from core.logging import logger
from .exceptions import EmailSendException

FROM_EMAIL = "noreply@send.comic-collection.com"

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to: str, template: dict) -> None:
    try:
        resend.Emails.send(
            {
            "from": f"{FROM_EMAIL}",
            "to": [to],
            "subject": template["subject"],
            "text": template["text"],
            "html": template["html"]
            }
        )
    except Exception as e:
        logger.debug(f"Email send failed: {e}")
        raise EmailSendException() from e