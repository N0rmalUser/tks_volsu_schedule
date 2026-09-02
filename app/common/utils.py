from datetime import datetime

from app.common.schedule_formater import ScheduleFormatter
from app.core.config import config
from app.core.constants import TZ
from app.schemas.enums import WEEK_MAP, Keyboard, WeekType
from app.services.schedule import ScheduleService


def get_today() -> tuple[int, WeekType]:
    """Метод для получения сегодняшнего дня и недели"""

    day = int(f"{datetime.now(TZ).weekday() + 1}")
    week_int = 2 if config.numerator == 0 else 1
    week = week_int if datetime.now(TZ).isocalendar()[1] % 2 == 0 else 3 - week_int
    if day == 7:
        return 1, WEEK_MAP[week + 1 if week == 1 else week - 1]

    return day, WEEK_MAP[week]


async def get_schedule(target: Keyboard, day: int, week: WeekType, value: int) -> str:
    text = "Ошибка. Напишите админу /admin"

    if target == Keyboard.TEACHER:
        lessons = await ScheduleService().get_teacher_full_schedule(teacher_id=value, day_of_week=day, week=week)
        text = ScheduleFormatter().teacher(
            day_of_week=day,
            week_type=week,
            entries=lessons,
        )
    elif target == Keyboard.STUDENT:
        lessons = await ScheduleService().get_group_schedule(group_id=value, day_of_week=day, week=week)
        text = ScheduleFormatter().group(
            day_of_week=day,
            week_type=week,
            entries=lessons,
        )
    elif target == Keyboard.ROOM:
        lessons = await ScheduleService().get_room_schedule(room_id=value, day_of_week=day, week=week)
        text = ScheduleFormatter().room(
            day_of_week=day,
            week_type=week,
            entries=lessons,
        )
    return text
