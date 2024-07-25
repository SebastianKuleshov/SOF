from sqlalchemy.orm import Mapped, mapped_column

from app.core.adapters.postgres.postgres_adapter import Base
from app.common.models_mixins import CreatedAtUpdatedAtMixin, int_pk


class UserModel(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'users'

    id: Mapped[int_pk]
    nick_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    biography: Mapped[str] = mapped_column(nullable=True)
    reputation: Mapped[int] = mapped_column(default=0)
