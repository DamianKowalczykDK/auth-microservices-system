from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import NameEmail


class EmailService:
    """
    Service responsible for sending application emails.

    This service wraps FastMail functionality and provides
    higher-level methods for sending common system emails
    such as activation messages.
    """

    def __init__(self, mailer: FastMail):
        """
        Initialize EmailService.

        Args:
            mailer (FastMail): Configured FastMail instance used to send emails.
        """
        self.mailer = mailer

    async def send_email(self, to: str, subject: str, html: str) -> None:
        """
        Send a generic HTML email.

        Args:
            to (str): Recipient email address.
            subject (str): Email subject line.
            html (str): HTML content of the email.

        Returns:
            None
        """
        message = MessageSchema(
            subject=subject,
            recipients=[NameEmail(email=to, name=to)],
            body=html,
            subtype=MessageType.html
        )

        await self.mailer.send_message(message)

    async def send_activation_email(self, email: str, token: str) -> None:
        """
        Send account activation email containing activation token.

        Args:
            email (str): Recipient email address.
            token (str): Activation token for account verification.

        Returns:
            None
        """
        html = f"<p>Your activation code {token}</p>"
        await self.send_email(email, "Activate your account", html)