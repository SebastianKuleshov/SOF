import datetime
from typing import Annotated

from sqlalchemy import DateTime, func, Integer
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


class SoftDeleteMixin:
    deleted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )


int_pk = Annotated[int, mapped_column(Integer, primary_key=True, index=True)]
