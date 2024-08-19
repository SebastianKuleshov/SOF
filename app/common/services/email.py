from email.message import EmailMessage

import aiosmtplib
from aiosmtplib.errors import SMTPException
from fastapi import HTTPException

from app.auth.schemas import EmailCreatePayloadSchema
from app.dependencies import get_settings

settings = get_settings()


class EmailService:
    def __init__(self):
        self.host = settings.EMAIL_SMTP_HOST
        self.port = settings.EMAIL_SMTP_PORT
        self.username = settings.EMAIL_SMTP_USERNAME
        self.password = settings.EMAIL_SMTP_PASSWORD
        self.use_tls = settings.EMAIL_SMTP_TLS

    async def send_email(
            self,
            email_schema: EmailCreatePayloadSchema,
            sender: str = None
    ) -> bool:
        if sender is None:
            sender = settings.EMAIL_SMTP_USERNAME

        message = EmailMessage()
        message["From"] = sender
        message["To"] = email_schema.recipient
        message["Subject"] = email_schema.subject
        message.set_content(email_schema.body)

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
