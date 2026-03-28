from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import NameEmail

class EmailService:
    def __init__(self, mailer: FastMail):
        self.mailer = mailer

    async def send_email(self, to: str, subject: str, html: str) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=[NameEmail(email=to, name=to)],
            body=html,
            subtype=MessageType.html
        )

        await self.mailer.send_message(message)

    async def send_activation_email(self, email: str, token: str) -> None:
        html=f"<p>Your activation code {token}</p>"
        await self.send_email(email, "Activate your account", html)


