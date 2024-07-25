import datetime

from pydantic import BaseModel


class CreatedAtUpdatedAtMixin(BaseModel):
    created_at: datetime.datetime
    updated_at: datetime.datetime
