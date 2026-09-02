from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.database.repository.user import UserRepository
from app.schemas.enums import Platform, UserRole
from app.schemas.user import UserInfo


class UserService:
    def __init__(self, session: AsyncSession, user: User):
        self.session = session
        self.repo = UserRepository(session)
        self.user = user

    @classmethod
    async def create(cls, session: AsyncSession, platform: Platform, user_id: int) -> "UserService":
        repo = UserRepository(session)
        user = await repo.get_or_create(platform=platform, platform_user_id=user_id)
        return cls(session, user)

    @classmethod
    async def from_tg_topic(
        cls,
        session: AsyncSession,
        tg_topic_id: int,
    ) -> "UserService | None":
        repo = UserRepository(session)

        user = await repo.get_by_tg_topic_id(
            tg_topic_id=tg_topic_id,
        )

        if user is None:
            return None

        return cls(session, user)

    async def get_user_role(self) -> UserRole:
        return self.user.role

    async def set_user_role(
        self,
        role: UserRole,
    ):
        await self.repo.update(
            user=self.user,
            role=role,
        )

    async def get_tg_topic_id(self) -> int | None:
        return self.user.tg_topic_id

    async def set_tg_topic_id(
        self,
        topic_id: int,
    ) -> None:
        self.user.tg_topic_id = topic_id
        await self.session.flush()

    async def get_tg_tracking(self) -> bool:
        return self.user.tg_tracking

    async def set_tg_tracking(
        self,
        tracking: bool,
    ):
        await self.repo.update(
            user=self.user,
            tg_tracking=tracking,
        )

        await self.session.flush()

    async def get_default_id(self) -> int | None:

        if self.user.role == UserRole.TEACHER:
            entity = self.user.default_teacher or self.user.teacher
        else:
            entity = self.user.default_group or self.user.group

        return entity.id if entity else None

    async def set_default_id(
        self,
        target_id: int,
    ) -> None:
        if self.user.role == UserRole.TEACHER:
            await self.repo.update(
                user=self.user,
                default_teacher_id=target_id,
            )
        else:
            await self.repo.update(
                user=self.user,
                default_group_id=target_id,
            )

        await self.session.flush()

    async def set_teacher(
        self,
        teacher_id: int,
    ):
        await self.repo.update(
            user=self.user,
            teacher_id=teacher_id,
        )

    async def set_group(self, group_id: int):
        await self.repo.update(
            user=self.user,
            group_id=group_id,
        )

    async def get_user_id(self) -> int:
        return self.user.platform_user_id

    async def get_id(self) -> int:
        return self.user.id

    async def set_bot_blocked(self, blocked: bool) -> None:
        await self.repo.update(
            user=self.user,
            bot_blocked=blocked,
        )
        await self.session.flush()

    async def get_user_info(self) -> UserInfo:
        group = self.user.group
        teacher = self.user.teacher
        group_name = group.name if group else None
        teacher_name = teacher.name if teacher else None

        return UserInfo(
            role=self.user.role,
            registered=self.user.created_at,
            group_name=group_name,
            teacher_name=teacher_name,
            tracking=self.user.tg_tracking,
            blocked=self.user.bot_blocked,
        )
