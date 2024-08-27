import datetime
from typing import Annotated

from sqlalchemy import DateTime, func, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtUpdatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now()
    )


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


int_pk = Annotated[int, mapped_column(Integer, primary_key=True, index=True)]

str_pk = Annotated[str, mapped_column(String, primary_key=True, index=True)]
