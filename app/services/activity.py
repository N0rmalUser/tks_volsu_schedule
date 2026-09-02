from datetime import date, datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Activity
from app.database.repository.activity import ActivityRepository
from app.schemas.enums import ActivityType


class ActivityService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.repository = ActivityRepository(session)

    async def add(
        self,
        *,
        user_id: int,
        action: ActivityType,
        group_id: int | None = None,
        teacher_id: int | None = None,
        room_id: int | None = None,
    ) -> Activity:
        return await self.repository.create(
            user_id=user_id,
            action=action,
            group_id=group_id,
            teacher_id=teacher_id,
            room_id=room_id,
        )

    async def get_activity_for_month(
        self,
        date_value: date,
    ) -> list[dict[str, date | int]]:
        end = datetime.combine(
            date_value + timedelta(days=1),
            time.min,
        )
        start = end - timedelta(days=30)

        counts = await self.repository.get_daily_counts(
            start=start,
            end=end,
        )

        return [
            {
                "date": day,
                "user_count": counts.get(day, 0),
            }
            for i in range(29, -1, -1)
            for day in [date_value - timedelta(days=i)]
        ]

    async def get_activity_for_day(
        self,
        date_value: date,
    ) -> list[dict[str, datetime | int]]:
        start = datetime.combine(date_value, time.min)
        end = start + timedelta(days=1)

        counts = await self.repository.get_hourly_counts(
            start=start,
            end=end,
        )

        return [
            {
                "hour": start + timedelta(hours=hour),
                "user_count": counts.get(
                    start + timedelta(hours=hour),
                    0,
                ),
            }
            for hour in range(24)
        ]
