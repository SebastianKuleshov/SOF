from typing import Text

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import int_pk, CreatedAtUpdatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base


class CommentModel(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'comments'

    id: Mapped[int_pk]
    body: Mapped[Text]
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey('questions.id', ondelete='CASCADE'),
        nullable=True
    )
    answer_id: Mapped[int] = mapped_column(
        ForeignKey('answers.id', ondelete='CASCADE'),
        nullable=True
    )

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        back_populates='comments',
        lazy='noload'
    )

    question: Mapped['QuestionModel'] = relationship(
        'QuestionModel',
        back_populates='comments',
        lazy='noload'
    )

    answer: Mapped['AnswerModel'] = relationship(
        'AnswerModel',
        back_populates='comments',
        lazy='noload'
    )


