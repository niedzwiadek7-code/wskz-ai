import pytest

from app.services.messages.prompts import (
    ASSIGN_MESSAGE_TO_SECTION_PROMPT,
    SEND_EMAIL_DESCRIPTION,
    USER_MESSAGE_PROMPT,
)
from app.services.route_agent.models import ToolCallResult


@pytest.mark.unit
def test_message_is_routed_successfully(client, fake_route_agent, mock_email_service):
    email = 'jan.nowak@example.com'
    message = (
        'Dzień dobry, Drukarka sieciowa na trzecim piętrze pokazuje błąd "brak papieru", '
        'mimo że papier jest włożony prawidłowo.'
    )

    fake_route_agent.tool_call_result = ToolCallResult(
        tool_name='send_email',
        params={
            'department': 'help desk',
            'subject': 'Drukarka sieciowa - błąd braku papieru',
            'body': message,
            'reply_to': email,
        },
        result=None,
    )

    response = client.post('/api/v1/messages', json={'email': email, 'message': message})

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['tool_result']['tool_name'] == 'send_email'
    assert data['tool_result']['params']['department'] == 'help desk'
    assert data['tool_result']['params']['reply_to'] == email
    assert data['tool_result']['result'] is None

    assert fake_route_agent.system_prompt == ASSIGN_MESSAGE_TO_SECTION_PROMPT
    assert fake_route_agent.tool.name == 'send_email'
    assert fake_route_agent.tool.description == SEND_EMAIL_DESCRIPTION
    assert fake_route_agent.message == USER_MESSAGE_PROMPT.format(email=email, message=message)
    mock_email_service.send.assert_not_called()
