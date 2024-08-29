from sqlalchemy.orm import Mapped, relationship

from app.common.models_mixins import int_pk, CreatedAtUpdatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base


class StorageItemModel(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'storage_items'

    id: Mapped[int_pk]
    original_file_name: Mapped[str]
    stored_file_name: Mapped[str]
    storage_path: Mapped[str]

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        back_populates='avatar_file_storage',
        lazy='noload'
    )
