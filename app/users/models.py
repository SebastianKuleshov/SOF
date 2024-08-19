from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.common.models_mixins import CreatedAtUpdatedAtMixin, int_pk
from app.core.adapters.postgres.postgres_adapter import Base
from app.roles.models import RoleModel

role_user = Table(
    'role_user',
    Base.metadata,
    Column(
        'role_id',
        ForeignKey('roles.id', ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        'user_id',
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
)


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

    votes: Mapped[list['VotesModel']] = relationship(
        'VotesModel',
        back_populates='user',
        lazy='noload',
        cascade='all, delete'
    )

    roles: Mapped[list[RoleModel]] = relationship(
        'RoleModel',
        secondary='role_user',
        back_populates='users',
        lazy='noload'
    )
