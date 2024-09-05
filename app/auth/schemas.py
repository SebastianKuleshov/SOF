from pydantic import BaseModel, EmailStr


class TokenBaseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class EmailCreateSchema(BaseModel):
    recipient: EmailStr


class EmailAttachmentSchema(BaseModel):
    content: str
    filename: str


class EmailCreatePayloadSchema(EmailCreateSchema):
    subject: str
    body: str
    attachments: list[EmailAttachmentSchema] | None = None
