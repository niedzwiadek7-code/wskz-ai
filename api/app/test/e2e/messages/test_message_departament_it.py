import os
import time

import httpx
import pytest

from app.routers.messages.models import Department
from app.services.email.base import EmailService, _normalise, _subject
from app.test.e2e.utils import parse_body

API_URL = os.getenv('E2E_API_URL', 'http://localhost:8000')

IT_DEPARTMENT_MESSAGE = (
    'Cześć, Nowy pracownik dołącza do zespołu w przyszły poniedziałek i będzie pracował zdalnie. '
    'Potrzebuje dostępu do wewnętrznej sieci firmowej przez VPN oraz uprawnień do repozytorium '
    "GitLab dla projektu 'core-api'. Proszę też o dodanie go do grupy AD 'developers' oraz "
    'skonfigurowanie dostępu do serwera stagingowego (SSH, klucz publiczny prześlę osobno). '
    'Dzięki, Paweł, Team Lead'
)


@pytest.mark.e2e
def test_message_departament_it(mail_server: EmailService):
    email = 'jan.nowak@example.com'

    response = httpx.post(
        f'{API_URL}/api/v1/messages',
        json={'email': email, 'message': IT_DEPARTMENT_MESSAGE},
        timeout=120,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['success'] is True

    result = data['tool_result']
    assert result['tool_name'] == 'send_email'
    assert result['params']['department'] == Department.IT
    assert result['params']['reply_to'] == email

    subject = result['params']['subject']
    body = result['params']['body']

    sent = None
    for _ in range(10):
        matches = [
            item
            for item in mail_server.get_messages(recipient='it@example.com')
            if _subject(item) == _normalise(subject)
        ]
        if matches:
            sent = matches[0]
            break
        time.sleep(0.5)

    assert sent is not None, f'No email to it@example.com with subject "{subject}" found in MailHog'
    assert _normalise(parse_body(sent)) == _normalise(body)
