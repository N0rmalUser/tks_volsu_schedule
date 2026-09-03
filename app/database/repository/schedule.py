from sqlalchemy import Sequence, delete, or_, select
from sqlalchemy.orm import joinedload

from app.core.config import config
from app.database.models.schedule import Room, Schedule
from app.database.repository.base import BaseRepository
from app.schemas.enums import GroupType, WeekType


class ScheduleRepository(BaseRepository):
    async def _get_schedule(
        self,
        filter_clause,
        day_of_week: int,
        week_type: WeekType,
        subgroup: int | None = None,
    ) -> list[Schedule]:

        conditions = [
            filter_clause,
            Schedule.day_of_week == day_of_week,
            Schedule.week_type.in_(
                [week_type, WeekType.EVERY],
            ),
        ]

        if subgroup is not None:
            conditions.append(
                or_(
                    Schedule.subgroup.is_(None),
                    Schedule.subgroup == subgroup,
                )
            )

        stmt = (
            select(Schedule)
            .where(*conditions)
            .options(
                joinedload(Schedule.group),
                joinedload(Schedule.teacher),
                joinedload(Schedule.subject),
                joinedload(Schedule.room),
            )
            .order_by(
                Schedule.lesson_number,
                Schedule.subgroup.asc().nulls_first(),
            )
        )

        result = await self.session.scalars(stmt)
        return list(result)

    async def get_group_schedule(self, *, group_id: int, day_of_week: int, week_type: WeekType, subgroup: int | None):
        return await self._get_schedule(Schedule.group_id == group_id, day_of_week, week_type, subgroup)

    async def get_teacher_schedule(self, *, teacher_id: int, day_of_week: int, week_type: WeekType):
        return await self._get_schedule(Schedule.teacher_id == teacher_id, day_of_week, week_type)

    async def get_room_schedule(self, *, room_id: int, room_name: str, day_of_week: int, week_type: WeekType):
        if room_name in config.parent_rooms:
            filter_clause = Schedule.room.has(Room.name.in_(config.parent_rooms[room_name]))
        else:
            filter_clause = Schedule.room_id == room_id
        return await self._get_schedule(filter_clause, day_of_week, week_type)

    async def add_schedule(
        self,
        entries: Sequence[Schedule],
    ) -> None:
        self.session.add_all(entries)
        await self.session.flush()

    async def clear_schedule(
        self,
        *,
        group_type: GroupType,
    ) -> None:
        await self.session.execute(
            delete(Schedule).where(
                Schedule.group_type == group_type,
            )
        )
        await self.session.flush()
