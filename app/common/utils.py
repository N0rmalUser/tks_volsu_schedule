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
    service = ScheduleService()
    formater = ScheduleFormatter()

    if target == Keyboard.TEACHER:
        teacher_name = await service.get_teacher_name(teacher_id=value)
        group_name = config.students.get(teacher_name)
        lessons = await service.get_teacher_schedule(teacher_id=value, day_of_week=day, week=week)
        if group_name:
            if "." not in group_name:
                subgroup = None
            else:
                group_name, subgroup = group_name.rsplit(".", 1)
            group_ids = await service.get_group_ids([group_name])
            group_lessons = await service.get_group_schedule(
                group_id=group_ids[group_name], day_of_week=day, week=week, subgroup=subgroup
            )
            lessons.extend(group_lessons)
        text = formater.teacher(
            teacher_name=teacher_name,
            day_of_week=day,
            week_type=week,
            entries=lessons,
        )
    elif target == Keyboard.STUDENT:
        group_name = await service.get_group_name(group_id=value)
        lessons = await service.get_group_schedule(group_id=value, day_of_week=day, week=week)
        text = formater.group(
            group_name=group_name,
            day_of_week=day,
            week_type=week,
            entries=lessons,
        )
    elif target == Keyboard.ROOM:
        group_name = await service.get_room_name(room_id=value)
        lessons = await service.get_room_schedule(room_id=value, day_of_week=day, week=week)
        text = formater.room(
            room_name=group_name,
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
