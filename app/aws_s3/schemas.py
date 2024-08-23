from pydantic import BaseModel


class S3FileBaseSchema(BaseModel):
    folder: str
    name: str
    user_id: int

class S3FileOutSchema(S3FileBaseSchema):
    id: int
