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
from datetime import datetime, timedelta

import pytz

from bot.config import ACTIVITIES_DB, TIMEZONE, USERS_DB
from bot.database.utils import sql_kit


@sql_kit(USERS_DB)
def get_last_hour_users(cursor: sqlite3.Cursor) -> list:
    """Возвращает список пользователей, которые были активны в течение предыдущего часа."""

    start_of_last_hour = datetime.now(pytz.timezone(TIMEZONE)).replace(
        minute=0, second=0, microsecond=0
    )
    end_of_last_hour = start_of_last_hour + timedelta(hours=1)

    cursor.execute(
        """
        SELECT user_id FROM User_Info
        WHERE last_date >= ? AND last_date < ?
    """,
        (
            start_of_last_hour.strftime("%d-%m-%Y %H:%M:%S"),
            end_of_last_hour.strftime("%d-%m-%Y %H:%M:%S"),
        ),
    )

    return [row[0] for row in cursor.fetchall()]


@sql_kit(ACTIVITIES_DB)
def update_user_activity_stats(cursor: sqlite3.Cursor):
    """Обновляет статистику активности пользователей за последний час. Удаляет данные из вспомогательной таблицы User_Unique_Activity, которые устарели на 2 часа."""

    two_hours_ago = datetime.now(pytz.timezone(TIMEZONE)).replace(
        minute=0, second=0, microsecond=0
    ) - timedelta(hours=25)

    cursor.execute(
        """
        DELETE FROM User_Unique_Activity
        WHERE date < ? OR (date = ? AND hour < ?)
        """,
        (
            two_hours_ago.strftime("%d-%m-%Y"),
            two_hours_ago.strftime("%d-%m-%Y"),
            two_hours_ago.hour,
        ),
    )

    active_users = get_last_hour_users()
    current_datetime = datetime.now(pytz.timezone("Europe/Moscow"))
    date_str = current_datetime.strftime("%d-%m-%Y")
    current_hour = current_datetime.hour

    cursor.executemany(
        """
        INSERT OR IGNORE INTO User_Unique_Activity (date, hour, user_id)
        VALUES (?, ?, ?)
    """,
        [(date_str, current_hour, user_id) for user_id in active_users],
    )

    cursor.execute(
        """
       SELECT COUNT(*) FROM User_Unique_Activity
       WHERE date = ? AND hour = ?
       """,
        (date_str, current_hour),
    )

    user_count = cursor.fetchone()[0]

    cursor.execute(
        """
       INSERT INTO User_Activity_Stats (date, hour, user_count)
       VALUES (?, ?, ?)
       ON CONFLICT(date, hour) DO UPDATE SET user_count = excluded.user_count
       """,
        (date_str, current_hour, user_count),
    )

    logging.info(
        f"Статистика активности пользователей за {current_datetime.strftime('%d-%m-%Y %H:%M')} обновлена"
    )


@sql_kit(ACTIVITIES_DB)
def fetch_user_activity_stats(cursor: sqlite3.Cursor):
    """Возвращает статистику активности пользователей за последние 24 часа."""

    cursor.execute("SELECT * FROM User_Activity_Stats")
    data = cursor.fetchall()
    return data
