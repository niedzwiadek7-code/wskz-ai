import pytest

from app.config import get_settings
from app.services.email.base import EmailService


@pytest.fixture()
def mail_server() -> EmailService:
    return EmailService(get_settings())


@pytest.fixture(autouse=True)
def clean_mail_server(mail_server: EmailService) -> None:
    mail_server.clear()
    yield
