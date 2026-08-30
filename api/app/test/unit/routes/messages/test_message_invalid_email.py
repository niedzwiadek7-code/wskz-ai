import pytest


@pytest.mark.unit
def test_invalid_email_returns_422(client):
    response = client.post(
        '/api/v1/messages',
        json={'email': 'not-an-email', 'message': 'treść wiadomości'},
    )

    assert response.status_code == 422
