from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.messages import base as messages_service


class FakeRouteAgentService:
    def __init__(self) -> None:
        self.system_prompt = None
        self.model_settings = None
        self.tool = None
        self.message = None
        self.tool_call_result = None

    def build_agent(self, system_prompt, tool, model_settings):
        self.system_prompt = system_prompt
        self.model_settings = model_settings
        self.tool = tool
        return self

    async def run(self, message):
        self.message = message
        return self.tool_call_result


@pytest.fixture
def fake_route_agent() -> FakeRouteAgentService:
    return FakeRouteAgentService()


@pytest.fixture
def mock_email_service() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(fake_route_agent, mock_email_service, monkeypatch):
    monkeypatch.setattr(messages_service, 'RouteAgentService', lambda settings: fake_route_agent)
    monkeypatch.setattr(messages_service, 'EmailService', lambda settings: mock_email_service)

    with TestClient(app) as test_client:
        yield test_client
