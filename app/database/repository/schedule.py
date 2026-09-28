from sqlalchemy import Sequence, delete, or_, select
from sqlalchemy.orm import joinedload

from app.core.config import config
from app.core.enums import GroupType, WeekType
from app.database.models.schedule import Room, Schedule
from app.database.repository.base import BaseRepository


class ScheduleRepository(BaseRepository):
    async def _get_schedule(
        self,
        filter_clause,
        day_of_week: int | None = None,
        week_type: WeekType | None = None,
        subgroup: int | None = None,
    ) -> list[Schedule]:
        conditions = [filter_clause]

        if day_of_week is not None:
            conditions.append(Schedule.day_of_week == day_of_week)

        if week_type is not None:
            week_types = (
                [WeekType.EVERY, WeekType.ODD, WeekType.EVEN]
                if week_type == WeekType.EVERY
                else [WeekType.EVERY, week_type]
            )
            conditions.append(Schedule.week_type.in_(week_types))

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
                Schedule.day_of_week,
                Schedule.lesson_number,
                Schedule.subgroup.asc().nulls_first(),
            )
        )

        result = await self.session.scalars(stmt)
        return list(result)

    async def get_group_schedule(
        self,
        *,
        group_id: int,
        day_of_week: int | None = None,
        week_type: WeekType | None = None,
        subgroup: int | None = None,
    ):
        return await self._get_schedule(Schedule.group_id == group_id, day_of_week, week_type, subgroup)

    async def get_teacher_schedule(
        self,
        *,
        teacher_id: int | None = None,
        day_of_week: int | None = None,
        week_type: WeekType | None = None,
    ):
        return await self._get_schedule(Schedule.teacher_id == teacher_id, day_of_week, week_type)

    async def get_room_schedule(
        self,
        *,
        room_id: int,
        room_name: str | None = None,
        day_of_week: int | None = None,
        week_type: WeekType | None = None,
    ):
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
