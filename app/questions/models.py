from typing import Text

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import CreatedAtUpdatedAtMixin, int_pk
from app.core.adapters.postgres.postgres_adapter import Base


class QuestionModel(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'questions'

    id: Mapped[int_pk]
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

    answers: Mapped[list['AnswerModel']] = relationship(
        'AnswerModel',
        back_populates='question',
        lazy='noload'
    )

    comments: Mapped[list['CommentModel']] = relationship(
        'CommentModel',
        back_populates='question',
        lazy='noload'
    )
