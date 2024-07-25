import datetime
from typing import Text

from sqlalchemy import func, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import IntPKMixin, CreatedAtUpdatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base


class QuestionModel(IntPKMixin, CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'questions'

    title: Mapped[str]
    body: Mapped[Text]
    accepted_answer_id: Mapped[int] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        back_populates='questions',
        lazy='noload'
    )

