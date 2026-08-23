# TKS VOLSU SCHEDULE BOT
# Copyright (C) 2024 N0rmalUser
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from dateutil.relativedelta import relativedelta

from app.config import USERS_DB
from app.database.user import User


def sql_kit(db: Path = ":memory:"):
    """
    Декоратор для работы с базой данных. Он открывает соединение с базой данных, выполняет функцию и закрывает
    соединение.
    :param db:  Путь к базе данных
    :return:  Результат выполнения функции
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db)
            try:
                result = func(*args, **kwargs, cursor=conn.cursor())
                conn.commit()
                return result
            finally:
                conn.close()

        return wrapper

    return decorator



def format_date(date: str) -> str:
    """Преобразует relativedelta в строку вида 'X лет, Y мес., Z дн.'"""

    from app.config import TZ

    date_and_time: datetime = datetime.fromisoformat(date)
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


def user_info(user_id: int) -> str:
    """Возвращает информацию о пользователе, подготовленную к отправке админу"""

    from app.config import config

    def safe_get(lst: list, idx: int) -> str:
        return lst[idx] if 0 <= idx < len(lst) else "Unknown"

    user = User(user_id)

    teacher = "None"
    if user.teacher:
        idx = int(user.teacher) - 1
        teacher = safe_get(config.teachers, idx)

    group = "None"
    if user.group:
        idx = int(user.group) - 1
        group = safe_get(config.groups, idx).replace("-", "")

    return f"""
Информация о {"СТУДЕНТ" if user.user_type == "student" else "ПРЕПОДАВАТЕЛ"}Е:
Дата регистрации:
    <code>{datetime.fromisoformat(user.start_date).strftime("%Y-%m-%d %H:%M:%S")}</code>
    <code>{format_date(user.start_date)}</code>
Последняя активность:
    <code>{datetime.fromisoformat(user.last_date).strftime("%Y-%m-%d %H:%M:%S")}</code>
    <code>{format_date(user.last_date)}</code>

<code>Заблокировал: </code> <code>{user.blocked}</code>
<code>Забанен:      </code> <code>{user.banned}</code>
<code>Отслеживается:</code> <code>{user.tracking}</code>
<code>Преподаватель:</code> <code>{teacher}</code>
<code>Группа:       </code> <code>{group}</code>
"""


# Не менять, должен обязательно список отправлять
@sql_kit(USERS_DB)
def all_user_ids(cursor: sqlite3.Cursor) -> list[int]:
    """
    Возвращает список всех user_id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`list` Список всех user_id
    """

    cursor.execute("SELECT user_id FROM User_Info")
    return [i[0] for i in cursor.fetchall()]


@sql_kit(USERS_DB)
def student_ids(cursor: sqlite3.Cursor) -> list[int]:
    """
    Возвращает список user_id всех студентов
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`list` Список всех user_id
    """

    cursor.execute("SELECT user_id FROM User_Info WHERE user_type = 'student'")
    return [i[0] for i in cursor.fetchall()]


@sql_kit(USERS_DB)
def teachers_ids(cursor: sqlite3.Cursor) -> list[int]:
    """
    Возвращает список user_id всех преподавателей
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`list` Список всех user_id
    """

    cursor.execute("SELECT user_id FROM User_Info WHERE user_type = 'teacher'")
    return [i[0] for i in cursor.fetchall()]


@sql_kit(USERS_DB)
def get_all_users_info(cursor: sqlite3.Cursor) -> str:
    """
    Возвращает информацию о всех пользователях, подготовленную к отправке админу
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` Информация о всех пользователях
    """

    users_count = len(all_user_ids())
    cursor.execute("SELECT last_date FROM User_Info")
    users = cursor.fetchall()
    month_users_count, week_users_count, today_users_count = 0, 0, 0
    today = datetime.today().date()
    for (last_date_str,) in users:
        last_date = datetime.fromisoformat(last_date_str).date()
        days_until = (last_date - today).days
        if days_until >= -30:
            month_users_count += 1
        if days_until >= -7:
            week_users_count += 1
        if days_until >= -1:
            today_users_count += 1

    cursor.execute("SELECT COUNT(*) FROM User_Info WHERE blocked = 1")
    blocked_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM User_Info WHERE banned = 1")
    banned_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM User_Info WHERE user_type = 'teacher'")
    teachers = cursor.fetchone()[0]

    return (
        f"Пользователей: {users_count}\n\n"
        f"Из них:\n"
        f"Преподавателей {teachers}\n"
        f"Студентов {int(users_count) - int(teachers)}\n\n"
        f"Активных:\n"
        f"За месяц - {month_users_count}\n"
        f"За неделю - {week_users_count}\n"
        f"За сутки - {today_users_count}\n"
        f"Заблокировали бота: {blocked_count}\n"
        f"Забанено: {banned_count}"
    )


async def tracking_manage(tracking: bool) -> None:
    """
    Включает или выключает отслеживание для всех пользователей
    :param tracking:  :class:`bool` True или False
    """

    for user_id in all_user_ids():
        User(user_id).tracking = tracking


async def get_tracked_users() -> list:
    """
    Возвращает список отслеживаемых пользователей
    :return:  :class:`list` Список отслеживаемых пользователей
    """

    user_ids = all_user_ids()
    return [f"`{user_id}`" for user_id in user_ids if User(user_id).tracking]


@sql_kit(USERS_DB)
def get_users_by_group_id(group_id: int, cursor: sqlite3.Cursor) -> str | None:
    cursor.execute(
        """
        SELECT u.user_id
        FROM User_Info u
        JOIN Temp_Data t ON u.user_id = t.user_id
        WHERE t.group_id = ?
        """,
        (group_id,),
    )
    return row[0] if (row := cursor.fetchone()) else None


@sql_kit(USERS_DB)
def get_users_by_teacher_id(group_id: int, cursor: sqlite3.Cursor) -> str | None:
    cursor.execute(
        """
        SELECT u.user_id
        FROM User_Info u
        JOIN Temp_Data t ON u.user_id = t.user_id
        WHERE t.teacher_id = ?
        """,
        (group_id,),
    )
    return row[0] if (row := cursor.fetchone()) else None

