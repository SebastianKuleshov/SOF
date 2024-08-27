from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.common.models_mixins import int_pk
from app.core.adapters.postgres.postgres_adapter import Base


class S3FileModel(Base):
    __tablename__ = 's3_files'

    id: Mapped[int_pk]
    folder: Mapped[str]
    name: Mapped[str]
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        back_populates='s3_files',
        lazy='noload'
    )
