import pytest


@pytest.mark.unit
def test_internal_service_error_returns_500(client, fake_route_agent):
    async def fail_run(*args, **kwargs):
        raise RuntimeError('Agent finished without calling the tool')

    fake_route_agent.run = fail_run

    response = client.post(
        '/api/v1/messages',
        json={'email': 'jan.nowak@example.com', 'message': 'treść wiadomości'},
    )

    assert response.status_code == 500
