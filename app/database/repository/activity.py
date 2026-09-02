from datetime import date, datetime

from sqlalchemy import func, select

from app.database.models import Activity
from app.database.repository.base import BaseRepository
from app.schemas.enums import ActivityType


class ActivityRepository(BaseRepository):
    async def create(
        self,
        *,
        user_id: int,
        action: ActivityType,
        group_id: int | None = None,
        teacher_id: int | None = None,
        room_id: int | None = None,
    ) -> Activity:
        activity = Activity(
            user_id=user_id,
            action=action,
            group_id=group_id,
            teacher_id=teacher_id,
            room_id=room_id,
        )

        self.session.add(activity)
        await self.session.flush()

        return activity

    async def get_daily_counts(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> dict[date, int]:
        day = func.date(Activity.created_at)

        stmt = (
            select(
                day.label("day"),
                func.count(func.distinct(Activity.user_id)).label("user_count"),
            )
            .where(
                Activity.created_at >= start,
                Activity.created_at < end,
            )
            .group_by(day)
            .order_by(day)
        )

        result = await self.session.execute(stmt)

        return {row.day: row.user_count for row in result}

    async def get_hourly_counts(
        self,
        *,
        start: datetime,
        end: datetime,
    ) -> dict[datetime, int]:
        hour = func.strftime(
            "%Y-%m-%d %H:00:00",
            Activity.created_at,
        )

        stmt = (
            select(
                hour.label("hour"),
                func.count(func.distinct(Activity.user_id)).label("user_count"),
            )
            .where(
                Activity.created_at >= start,
                Activity.created_at < end,
            )
            .group_by(hour)
            .order_by(hour)
        )

        result = await self.session.execute(stmt)

        return {datetime.strptime(row.hour, "%Y-%m-%d %H:00:00"): row.user_count for row in result}
