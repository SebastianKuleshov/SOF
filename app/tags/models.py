from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.common.models_mixins import int_pk, CreatedAtMixin
from app.core.adapters.postgres.postgres_adapter import Base


class TagModel(CreatedAtMixin, Base):
    __tablename__ = 'tags'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(unique=True)

    questions: Mapped[list['QuestionModel']] = relationship(
        'QuestionModel',
        secondary='question_tag',
        back_populates='tags',
        lazy='noload'
    )
