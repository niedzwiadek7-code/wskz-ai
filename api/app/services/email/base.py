import smtplib
from email.message import EmailMessage

from app.config import Settings


class EmailService:
    def __init__(
        self,
        settings: Settings,
    ):
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._from = settings.email_from

    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        reply_to: str,
    ) -> None:
        message = EmailMessage()

        message['From'] = self._from
        message['To'] = recipient
        message['Reply-To'] = reply_to
        message['Subject'] = subject

        message.set_content(body)

        with smtplib.SMTP(self._host, self._port) as smtp:
            smtp.send_message(message)
