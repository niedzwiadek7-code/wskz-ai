import re
import smtplib
from email.header import decode_header
from email.message import EmailMessage

import httpx

from app.config import Settings


def _decode_subject(value: str) -> str:
    parts = decode_header(value)
    decoded = []
    for text, charset in parts:
        if isinstance(text, bytes):
            try:
                decoded.append(text.decode(charset or 'utf-8'))
            except (LookupError, UnicodeDecodeError):
                decoded.append(text.decode('utf-8', errors='replace'))
        else:
            decoded.append(text)
    return ''.join(decoded)


def _normalise(value: str) -> str:
    return re.sub(r'\s+', ' ', value).strip()


def _subject(item: dict) -> str:
    return _normalise(_decode_subject(' '.join(item.get('Content', {}).get('Headers', {}).get('Subject') or [])))


class EmailService:
    def __init__(
        self,
        settings: Settings,
    ):
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._from = settings.email_from
        self._provider = settings.e2e_mail_provider
        self._inspect_url = settings.e2e_mailhog_url

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

    def get_messages(self, recipient: str) -> list[dict]:
        if self._provider == 'mailhog':
            response = httpx.get(f'{self._inspect_url}/api/v2/messages', timeout=30)
            response.raise_for_status()
            return [
                item
                for item in response.json().get('items', [])
                if recipient in (item.get('Content', {}).get('Headers', {}).get('To') or [])
            ]

        raise ValueError(f'Provider {self._provider!r} does not support inbox inspection')

    def clear(self) -> None:
        if self._provider == 'mailhog':
            httpx.delete(f'{self._inspect_url}/api/v1/messages', timeout=30).raise_for_status()
            return

        raise ValueError(f'Provider {self._provider!r} does not support inbox inspection')
