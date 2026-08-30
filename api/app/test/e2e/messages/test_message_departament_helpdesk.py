import os
import time

import httpx
import pytest

from app.services.email.base import EmailService, _normalise, _subject
from app.services.messages.models import Department
from app.test.e2e.utils import parse_body

API_URL = os.getenv('E2E_API_URL', 'http://localhost:8000')

HELPDESK_MESSAGE = (
    'Dzień dobry, Drukarka sieciowa na trzecim piętrze (ta obok kuchni) pokazuje '
    "błąd 'brak papieru', mimo że papier jest włożony prawidłowo. Próbowałam już "
    'wyjąć i włożyć tackę ponownie oraz zrestartować drukarkę przyciskiem z przodu, '
    'ale komunikat się powtarza. Kilka osób z zespołu też zgłaszało ten sam problem '
    'w tym tygodniu. Pozdrawiam, Kasia z Marketingu'
)


@pytest.mark.e2e
def test_message_departament_helpdesk(mail_server: EmailService):
    email = 'jan.nowak@example.com'

    response = httpx.post(
        f'{API_URL}/api/v1/messages',
        json={'email': email, 'message': HELPDESK_MESSAGE},
        timeout=120,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['success'] is True

    result = data['tool_result']
    assert result['tool_name'] == 'send_email'
    assert result['params']['department'] == Department.HELP_DESK
    assert result['params']['reply_to'] == email

    subject = result['params']['subject']
    body = result['params']['body']

    sent = None
    for _ in range(10):
        matches = [
            item
            for item in mail_server.get_messages(recipient='help-desk@example.com')
            if _subject(item) == _normalise(subject)
        ]
        if matches:
            sent = matches[0]
            break
        time.sleep(0.5)

    assert sent is not None, f'No email to help-desk@example.com with subject "{subject}" found in MailHog'
    assert _normalise(parse_body(sent)) == _normalise(body)
