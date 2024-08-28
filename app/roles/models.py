from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models_mixins import int_pk, CreatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base
from app.permissions.models import PermissionModel

permission_role = Table(
    'permission_role',
    Base.metadata,
    Column(
        'permission_id',
        ForeignKey('permissions.id', ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        'role_id',
        ForeignKey('roles.id', ondelete='CASCADE'),
        primary_key=True
    )
)


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

    permissions: Mapped[list['PermissionModel']] = relationship(
        'PermissionModel',
        secondary='permission_role',
        back_populates='roles',
        lazy='noload'
    )
