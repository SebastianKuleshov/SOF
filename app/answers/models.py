from typing import Text

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import int_pk, CreatedAtUpdatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base


class AnswerVoteModel(Base):
    __tablename__ = 'answer_vote'

    answer_id: Mapped[int] = mapped_column(
        ForeignKey('answers.id', ondelete='CASCADE'),
        primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    is_upvote: Mapped[bool]

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        back_populates='answer_votes',
        lazy='noload'
    )

    answer: Mapped['AnswerModel'] = relationship(
        'AnswerModel',
        back_populates='votes',
        lazy='noload'
    )


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

    votes: Mapped[list['AnswerVoteModel']] = relationship(
        'AnswerVoteModel',
        back_populates='answer',
        lazy='noload'
    )
