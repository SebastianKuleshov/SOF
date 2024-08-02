from typing import Text

from sqlalchemy import ForeignKey, Table, Column, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import CreatedAtUpdatedAtMixin, int_pk
from app.core.adapters.postgres.postgres_adapter import Base

question_tag = Table(
    'question_tag',
    Base.metadata,
    Column(
        'question_id',
        ForeignKey('questions.id', ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        'tag_id',
        ForeignKey('tags.id', ondelete='CASCADE'),
        primary_key=True
    )
)


class QuestionVoteModel(Base):
    __tablename__ = 'question_vote'

    question_id: Mapped[int] = mapped_column(
        ForeignKey('questions.id', ondelete='CASCADE'),
        primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    is_upvote: Mapped[bool]

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        back_populates='question_votes',
        lazy='noload'
    )

    question: Mapped['QuestionModel'] = relationship(
        'QuestionModel',
        back_populates='votes',
        lazy='noload'
    )


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

    tags: Mapped[list['TagModel']] = relationship(
        'TagModel',
        secondary='question_tag',
        back_populates='questions',
        lazy='noload'
    )

    votes: Mapped[list['QuestionVoteModel']] = relationship(
        'QuestionVoteModel',
        back_populates='question',
        lazy='noload'
    )
