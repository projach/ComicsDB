import resend
import os

FROM_EMAIL = "noreply@send.comic-collection.com"

resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to: str, template: dict) -> None:
    resend.Emails.send(
        {
        "from": f"{FROM_EMAIL}",
        "to": [to],
        "subject": template["subject"],
        "text": template["text"],
        "html": template["html"]
        }
    )