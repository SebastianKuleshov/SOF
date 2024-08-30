from abc import ABC, abstractmethod
from datetime import datetime
from typing import Annotated, Sequence, List

from fastapi import HTTPException, Depends
from sqlalchemy import select, update, insert, delete, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.types import MODEL, SCHEMA
from app.core.adapters.postgres.postgres_adapter import get_session


class BaseRepository(ABC):
    @property
    @abstractmethod
    def model(self):
        """ Generic SQLA DeclarativeMeta type, which is used as a base return type for repositories methods.
        Obligatory to redefine in a child class to substitute with an appropriate model child repositories works with
        Usage:: model = UserModel """
        return MODEL

    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_session)]
    ) -> None:
        self.session = session

    def _get_default_stmt(self) -> Select:
        """
        Returns the default SQLAlchemy select
        statement for the repository's model.

        This method provides a basic select statement
        for the model associated with the repository.
        It can be overridden in child classes to
        include additional query options as needed.

        Usage:

            def _get_default_stmt(self) -> Select:
                return select(self.model).options(joinedload(self.model.user))
        """
        return select(self.model)

    async def get_one(
            self,
            filters: dict
    ) -> MODEL | None:
        return await self.session.scalar(
            select(self.model).filter_by(**filters)
        )

    async def get_one_with_joins(
            self,
            filters: dict
    ) -> MODEL | None:
        stmt = self._get_default_stmt()
        return await self.session.scalar(stmt.filter_by(**filters))

    async def get_by_id(
            self,
            entity_id: int | str
    ) -> MODEL | None:
        return await self.session.get(self.model, entity_id)

    async def get_by_id_with_joins(
            self,
            entity_id: int | str
    ) -> MODEL | None:
        stmt = self._get_default_stmt()
        return await self.session.scalar(stmt.filter_by(id=entity_id))

    async def get_multi(
            self,
            offset: int = 0,
            limit: int = 100
    ) -> Sequence[MODEL]:
        entities = await self.session.scalars(
            select(self.model).offset(offset).limit(limit)
        )

        return entities.all()

    async def get_multi_with_joins(
            self,
            filters: dict = None,
            offset: int = 0,
            limit: int = 100
    ) -> Sequence[MODEL]:
        stmt = self._get_default_stmt()
        if filters:
            stmt = stmt.filter_by(**filters)
        entities = await self.session.scalars(stmt.offset(offset).limit(limit))
        entities = entities.unique().all()
        return entities

    async def get_entity_if_exists(
            self,
            entity_id: int | str
    ) -> MODEL | None:
        entity = await self.get_by_id(entity_id)
        if not entity:
            entity_name = self.model.__name__.replace('Model', '')
            raise HTTPException(
                status_code=404,
                detail=f'{entity_name} not found'
            )
        return entity

    async def get_entities_if_exists(
            self,
            entity_ids: List[int]
    ) -> Sequence[MODEL]:
        entities = await self.session.scalars(
            select(self.model).where(self.model.id.in_(entity_ids))
        )
        entities = entities.all()
        if len(entity_ids) != len(entities):
            entity_name = self.model.__name__.replace('Model', 's')
            raise HTTPException(
                status_code=404,
                detail=f'One of the {entity_name} not found'
            )
        return entities

    async def create(
            self,
            entity: SCHEMA
    ) -> MODEL:
        entity_model = self.model(**entity.model_dump())
        self.session.add(entity_model)
        await self.session.commit()
        await self.session.refresh(entity_model)

        return entity_model

    async def create_many(
            self,
            entities: List[SCHEMA]
    ) -> Sequence[MODEL]:
        entities_db = await self.session.scalars(
            insert(self.model).returning(self.model), entities
        )
        await self.session.commit()

        return entities_db.all()

    async def update(
            self,
            entity_id: int | str,
            entity: SCHEMA | dict,
            exclude_unset: bool = True
    ) -> SCHEMA:
        stmt = (
            update(self.model).
            where(self.model.id == entity_id)
        )
        stmt = stmt.values(**entity) if isinstance(
            entity, dict
        ) else stmt.values(
            **entity.model_dump(exclude_unset=exclude_unset)
        )
        result = await self.session.execute(stmt)
        if result is None:
            raise HTTPException(404, "Entity not found.")

        await self.session.commit()

        return entity

    async def update_many(
            self,
            entities: List[SCHEMA]
    ) -> bool:
        for entity in entities:
            await self.update(entity.id, entity)

        return True

    async def soft_delete(
            self,
            entity_id: int | str
    ) -> bool:
        stmt = update(self.model).where(self.model.id == entity_id).values(
            {"deleted_at": datetime.now()}
        )
        result = await self.session.execute(stmt)
        if result is None:
            raise HTTPException(404, "Entity not found.")
        await self.session.commit()

        return result == 1

    async def delete(
            self,
            entity_id: int | str
    ) -> bool:
        stmt = delete(self.model).where(self.model.id == entity_id)
        await self.session.execute(stmt)
        await self.session.commit()

        return True

    async def delete_many(
            self,
            entity_ids: List[int | str]
    ) -> bool:
        stmt = delete(self.model).where(self.model.id.in_(entity_ids))
        await self.session.execute(stmt)
        await self.session.commit()

        return True

    async def expire_session_for_entity(
            self,
            model: MODEL
    ) -> None:
        return self.session.expire(model)

    async def expire_session_for_all(
            self
    ) -> None:
        return self.session.expire_all()
