from pydantic import BaseModel


class TokenBaseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
