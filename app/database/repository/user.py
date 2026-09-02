from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database.models import User
from app.database.repository.base import BaseRepository
from app.schemas.enums import Platform


class UserRepository(BaseRepository):
    async def get(
        self,
        *,
        platform: Platform,
        platform_user_id: int,
    ) -> User | None:
        stmt = (
            select(User)
            .where(
                User.platform == platform,
                User.platform_user_id == platform_user_id,
            )
            .options(
                joinedload(User.group),
                joinedload(User.teacher),
                joinedload(User.default_group),
                joinedload(User.default_teacher),
            )
        )

        return await self.session.scalar(stmt)

    async def add(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_or_create(
        self,
        *,
        platform: Platform,
        platform_user_id: int,
    ) -> User:
        user = await self.get(
            platform=platform,
            platform_user_id=platform_user_id,
        )

        if user:
            return user

        return await self.add(
            User(
                platform=platform,
                platform_user_id=platform_user_id,
            )
        )

    async def get_by_tg_topic_id(
        self,
        tg_topic_id: int,
    ) -> User | None:
        stmt = select(User).where(
            User.tg_topic_id == tg_topic_id,
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self,
        *,
        user: User,
        **kwargs,
    ) -> None:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise ValueError(f"У модели User нет поля {key}")
