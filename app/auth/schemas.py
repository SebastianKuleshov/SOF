from pydantic import BaseModel


class TokenBaseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class EmailCreateSchema(BaseModel):
    recipient: str


class EmailCreatePayloadSchema(EmailCreateSchema):
    subject: str
    body: str
