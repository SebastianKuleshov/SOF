from typing import Text

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import CreatedAtUpdatedAtMixin, int_pk, \
    CreatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base


class QuestionTagModel(Base, CreatedAtMixin):
    __tablename__ = 'question_tag'

    question_id: Mapped[int] = mapped_column(
        ForeignKey('questions.id', ondelete='CASCADE'),
        primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey('tags.id', ondelete='CASCADE'),
        primary_key=True
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

    votes: Mapped[list['VotesModel']] = relationship(
        'VotesModel',
        back_populates='question',
        lazy='noload'
    )
