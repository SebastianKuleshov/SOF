from typing import Text

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import int_pk, CreatedAtUpdatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base


class AnswerModel(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'answers'
    __table_args__ = (UniqueConstraint('question_id', 'user_id'),)

    id: Mapped[int_pk]
    body: Mapped[Text]
    question_id: Mapped[int] = mapped_column(
        ForeignKey('questions.id', ondelete='CASCADE')
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        back_populates='answers',
        lazy='noload'
    )

    question: Mapped['QuestionModel'] = relationship(
        'QuestionModel',
        back_populates='answers',
        lazy='noload'
    )

    comments: Mapped[list['CommentModel']] = relationship(
        'CommentModel',
        back_populates='answer',
        lazy='noload'
    )

    votes: Mapped[list['VotesModel']] = relationship(
        'VotesModel',
        back_populates='answer',
        lazy='noload'
    )
