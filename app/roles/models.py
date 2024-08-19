from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import int_pk, CreatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base


class RoleModel(CreatedAtMixin, Base):
    __tablename__ = 'roles'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)

    users: Mapped[list['UserModel']] = relationship(
        'UserModel',
        secondary='role_user',
        back_populates='roles',
        lazy='noload'
    )
