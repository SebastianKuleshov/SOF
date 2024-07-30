import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.common.models_mixins import int_pk
from app.core.adapters.postgres.postgres_adapter import Base


class TagModel(Base):
    __tablename__ = 'tags'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    questions: Mapped[list['QuestionModel']] = relationship(
        'QuestionModel',
        secondary='question_tag',
        back_populates='tags',
        lazy='noload'
    )
