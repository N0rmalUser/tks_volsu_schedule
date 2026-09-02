from datetime import datetime
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta

from app.core.constants import TZ
from app.services.user import UserService


if TYPE_CHECKING:
    from app.schemas.user import UserInfo


def format_date(date_and_time: datetime) -> str:
    """Преобразует relativedelta в строку вида 'X лет, Y мес., Z дн.'"""

    if date_and_time.tzinfo is None:
        date_and_time = TZ.localize(date_and_time)
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
