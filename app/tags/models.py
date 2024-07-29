from sqlalchemy.orm import Mapped

from app.common.models_mixins import CreatedAtUpdatedAtMixin, int_pk
from app.core.adapters.postgres.postgres_adapter import Base


class TagModel(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'tags'

    id: Mapped[int_pk]
    name: Mapped[str]
