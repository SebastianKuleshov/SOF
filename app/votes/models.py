from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import int_pk
from app.core.adapters.postgres.postgres_adapter import Base


class VotesModel(Base):
    __tablename__ = 'votes'
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'question_id', 'answer_id', name='unique_user_vote'
        ),
    )

    id: Mapped[int_pk]
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
    is_upvote: Mapped[bool]

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        back_populates='votes',
        lazy='noload'
    )

    question: Mapped['QuestionModel'] = relationship(
        'QuestionModel',
        back_populates='votes',
        lazy='noload'
    )

    answer: Mapped['AnswerModel'] = relationship(
        'AnswerModel',
        back_populates='votes',
        lazy='noload'
    )
