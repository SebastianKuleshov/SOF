from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.common.models_mixins import CreatedAtUpdatedAtMixin, int_pk
from app.core.adapters.postgres.postgres_adapter import Base


class UserModel(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'users'

    id: Mapped[int_pk]
    nick_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    biography: Mapped[str] = mapped_column(nullable=True)
    reputation: Mapped[int] = mapped_column(default=0)

    questions: Mapped[list['QuestionModel']] = relationship(
        'QuestionModel',
        back_populates='user',
        lazy='noload',
        cascade='all, delete'
    )

    answers: Mapped[list['AnswerModel']] = relationship(
        'AnswerModel',
        back_populates='user',
        lazy='noload',
        cascade='all, delete'
    )

    comments: Mapped[list['CommentModel']] = relationship(
        'CommentModel',
        back_populates='user',
        lazy='noload',
        cascade='all, delete'
    )

    question_votes: Mapped[list['QuestionVoteModel']] = relationship(
        'QuestionVoteModel',
        back_populates='user',
        lazy='noload',
        cascade='all, delete'
    )

    answer_votes: Mapped[list['AnswerVoteModel']] = relationship(
        'AnswerVoteModel',
        back_populates='user',
        lazy='noload',
        cascade='all, delete'
    )
