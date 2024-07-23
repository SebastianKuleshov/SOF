from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeMeta

MODEL = TypeVar("MODEL", bound=DeclarativeMeta)
SCHEMA = TypeVar('SCHEMA', bound=BaseModel)
