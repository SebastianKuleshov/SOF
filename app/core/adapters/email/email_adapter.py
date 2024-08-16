from email.message import EmailMessage

import aiosmtplib
from aiosmtplib.errors import SMTPException
from fastapi import HTTPException

from app.dependencies import get_settings

settings = get_settings()


class EmailAdapter:
    def __init__(self):
        self.host = settings.EMAIL_SMTP_HOST
        self.port = settings.EMAIL_SMTP_PORT
        self.username = settings.EMAIL_SMTP_USERNAME
        self.password = settings.EMAIL_SMTP_PASSWORD
        self.use_tls = settings.EMAIL_SMTP_TLS

    async def send_email(
            self, subject: str, recipient: str, body: str, sender: str = None
    ) -> bool:
        if sender is None:
            sender = settings.EMAIL_SMTP_USERNAME

        message = EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls
            )
        except SMTPException:
            raise HTTPException(
                status_code=400,
                detail='Failed to send email'
            )

        return True


email_adapter = EmailAdapter()


async def get_email_adapter() -> EmailAdapter:
    yield email_adapter
