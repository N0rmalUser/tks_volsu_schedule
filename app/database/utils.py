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

import sqlite3
from datetime import datetime
from functools import wraps

from app.config import USERS_DB
from app.database.user import UserDatabase


def sql_kit(db=":memory:"):
    """
    Декоратор для работы с базой данных. Он открывает соединение с базой данных, выполняет функцию и закрывает соединение.
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


def user_info(user_id: int):
    """Возвращает информацию о пользователе, подготовленную к отправке админу"""

    user = UserDatabase(user_id)
    days_until = (
        datetime.strptime(user.last_date, "%d-%m-%Y %H:%M:%S").date() - datetime.today().date()
    ).days
    return f"""
Информация о пользователе:
<code>user type:  </code> <code>{user.type}</code>
<code>username:   </code> <code>{user.username}</code>
<code>fullname:   </code> <code>{user.fullname}</code>
<code>start date: </code> <code>{user.start_date}</code>
<code>last_date:  </code> <code>{user.last_date}</code>
<code>            </code> <code>{days_until} дней назад</code>

<code>inviter id: </code> <code>{user.inviter_id}</code>
<code>blocked:    </code> <code>{user.blocked}</code>
<code>banned:     </code> <code>{user.banned}</code>
<code>tracking:   </code> <code>{user.tracking}</code>
<code>teacher:    </code> <code>{user.teacher}</code>
<code>group:      </code> <code>{user.group.replace("-", "") if user.group else "None"}</code>
    """


@sql_kit(USERS_DB)
def all_user_ids(cursor: sqlite3.Cursor) -> list:
    """
    Возвращает список всех user_id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`list` Список всех user_id
    """

    cursor.execute("SELECT user_id FROM User_Info")
    return [row[0] for row in cursor.fetchall()]


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
        last_date = datetime.strptime(last_date_str, "%d-%m-%Y %H:%M:%S").date()
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

    result = (
        f"Пользователей: {users_count}\n\n"
        f"Из них:\n"
        f"Преподавателей {teachers}\n"
        f"Студентов {int(users_count) - int(teachers)}\n\n"
        f"Активных:\n"
        f"За месяц - {month_users_count}\n"
        f"За неделю - {week_users_count}\n"
        f"За день - {today_users_count}\n"
        f"Заблокировали бота: {blocked_count}\n"
        f"Забанено: {banned_count}"
    )
    return result


async def tracking_manage(tracking: bool) -> None:
    """
    Включает или выключает отслеживание для всех пользователей
    :param tracking:  :class:`bool` True или False
    """

    for user_id in all_user_ids():
        UserDatabase(user_id).tracking = tracking


async def get_tracked_users() -> list:
    """
    Возвращает список отслеживаемых пользователей
    :return:  :class:`list` Список отслеживаемых пользователей
    """

    user_ids = all_user_ids()
    tracked_users = []
    for user_id in user_ids:
        if UserDatabase(user_id).tracking:
            tracked_users.append(f"`{user_id}`")
    return tracked_users
