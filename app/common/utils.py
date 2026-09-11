from datetime import datetime

from dateutil.relativedelta import relativedelta

from app.common.schedule_formater import ScheduleFormatter
from app.core.config import config
from app.core.constants import TZ, WEEK_MAP
from app.core.enums import Keyboard, WeekType
from app.schemas.user import UserInfo
from app.services.schedule import ScheduleService
from app.services.user import UserService


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


def format_date(date_and_time: datetime) -> str:
    """Преобразует relativedelta в строку вида 'X лет, Y мес., Z дн.'"""

    if date_and_time.tzinfo is None:
        date_and_time = date_and_time.replace(tzinfo=TZ)
    rd = relativedelta(datetime.now(TZ), date_and_time)
    parts = [
        (rd.years, "лет"),
        (rd.months, "мес."),
        (rd.days, "дн."),
        (rd.hours, "ч"),
        (rd.minutes, "мин"),
        (rd.seconds, "сек"),
    ]
    # оставляем только ненулевые элементы
    result = [f"{value} {name}" for value, name in parts if value]
    return ", ".join(result) if result else "Только что"


async def user_info(service: UserService) -> str:
    """Возвращает информацию о пользователе, подготовленную к отправке админу"""

    def safe_get(lst: list, idx: int) -> str:
        return lst[idx] if 0 <= idx < len(lst) else "Unknown"

    info: UserInfo = await service.get_user_info()

    return f"""
Информация о {"СТУДЕНТ" if info.role == "student" else "ПРЕПОДАВАТЕЛ"}Е:
Дата регистрации:
    <code>{info.registered.strftime("%Y-%m-%d %H:%M:%S")}</code>
    <code>{format_date(info.registered)}</code>

<code>Заблокировал: </code> <code>{info.blocked}</code>
<code>Отслеживается:</code> <code>{info.tracking}</code>
<code>Преподаватель:</code> <code>{info.teacher_name}</code>
<code>Группа:       </code> <code>{info.group_name}</code>
"""
