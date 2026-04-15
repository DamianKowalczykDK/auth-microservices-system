from unittest.mock import MagicMock
from fastapi_mail import FastMail
from users.services.email_service import EmailService


async def test_email_service_send_email() -> None:
    mock_mailer = MagicMock(spec=FastMail)
    service = EmailService(mock_mailer)

    await service.send_activation_email("test_email@example.com", "token")

    mock_mailer.send_message.assert_called_once()
    args = mock_mailer.send_message.call_args[0][0]

    assert "Activate your account" in args.subject


