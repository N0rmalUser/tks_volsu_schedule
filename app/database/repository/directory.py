from app.database.models.schedule import Group, Room, Subject, Teacher
from app.database.repository.base import BaseRepository


class DirectoryRepository(BaseRepository):
    """Репозиторий для справочников: группы, преподаватели, предметы, аудитории."""

    async def get_groups(self, names):
        return await self.get_by_names(Group, names)

    async def get_teachers(self, names):
        return await self.get_by_names(Teacher, names)

    async def get_subjects(self, names):
        return await self.get_by_names(Subject, names)

    async def get_rooms(self, names):
        return await self.get_by_names(Room, names)

    async def add_groups(self, groups):
        await self.add_many(groups)

    async def add_teachers(self, teachers):
        await self.add_many(teachers)

    async def add_subjects(self, subjects):
        await self.add_many(subjects)

    async def add_rooms(self, rooms):
        await self.add_many(rooms)

    async def get_group_by_id(self, group_id: int) -> type[Group] | None:
        return await self.session.get(Group, group_id)

    async def get_teacher_by_id(self, teacher_id: int) -> type[Teacher] | None:
        return await self.session.get(Teacher, teacher_id)

    async def get_room_by_id(self, room_id: int) -> type[Room] | None:
        return await self.session.get(Room, room_id)
