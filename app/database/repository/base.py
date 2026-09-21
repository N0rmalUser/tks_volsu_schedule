from typing import TypeVar

from sqlalchemy import Sequence, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_names(self, model: type[T], names: Sequence[str]) -> list[T]:
        if not names:
            return []

        result = await self.session.scalars(select(model).where(model.name.in_(names)))

        return list(result.all())

    async def add_many(self, entities: Sequence) -> None:
        if not entities:
            return
        self.session.add_all(entities)

    async def delete_all(self, model: type[T]) -> None:
        await self.session.execute(delete(model))
