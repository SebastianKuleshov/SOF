from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import int_pk
from app.core.adapters.postgres.postgres_adapter import Base


class PermissionModel(Base):
    __tablename__ = 'permissions'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)

    roles: Mapped[list['RoleModel']] = relationship(
        'RoleModel',
        secondary='permission_role',
        back_populates='permissions',
        lazy='noload'
    )
