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
from datetime import datetime, timedelta

import pandas as pd
from pytz import timezone as tz

from app.config import ACTIVITIES_DB, TIMEZONE
from app.database.utils import sql_kit


@sql_kit(ACTIVITIES_DB)
def get_activity_for_month(date_str: str, cursor: sqlite3.Cursor):
    """Возвращает статистику активности пользователей за месяц по дням."""

    date = datetime.strptime(date_str, "%Y-%m-%d")
    daily_data = {}
    date_range = range(29, -1, -1)
    for i in date_range:
        day = date - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        cursor.execute("SELECT user_ids FROM daily_activity WHERE date = ?", (day_str,))
        result = cursor.fetchone()

        if result:
            user_ids = result[0].split(",")
            daily_data[day_str] = len(user_ids)
        else:
            daily_data[day_str] = 0
    return pd.DataFrame(list(daily_data.items()), columns=["Date", "User Count"])


@sql_kit(ACTIVITIES_DB)
def get_activity_for_day(date_str: str, cursor: sqlite3.Cursor):
    """Возвращает статистику активности пользователей за день по часам."""

    date = datetime.strptime(date_str, "%Y-%m-%d")
    hourly_data = {}
    for hour in range(24):
        hour_str = (date + timedelta(hours=hour)).strftime("%Y-%m-%d %H:00")
        cursor.execute("SELECT user_ids FROM hourly_activity WHERE datetime = ?", (hour_str,))
        result = cursor.fetchone()

        if result:
            user_ids = result[0].split(",")
            hourly_data[hour_str] = len(user_ids)
        else:
            hourly_data[hour_str] = 0
    return pd.DataFrame(list(hourly_data.items()), columns=["Hour", "User Count"])


@sql_kit(ACTIVITIES_DB)
def get_top_users_by_days(
    period: str = "all",
    month_str: str | None = None,
    year_str: str | None = None,
    cursor: sqlite3.Cursor | None = None,
):
    user_day_count = {}
    query = "SELECT date, user_ids FROM daily_activity"
    params = ()
    if period == "month" and month_str:
        query += " WHERE date LIKE ?"
        params = (month_str + "%",)
    elif period == "year" and year_str:
        query += " WHERE date LIKE ?"
        params = (year_str + "%",)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    for row in rows:
        user_ids = row[1].split(",")
        for user_id in user_ids:
            user_day_count[user_id] = user_day_count.get(user_id, 0) + 1
    df = pd.DataFrame(list(user_day_count.items()), columns=["User ID", "Days Active"])
    return df.sort_values(by="Days Active", ascending=False)


@sql_kit(ACTIVITIES_DB)
def get_top_users_by_hours(
    period: str = "all",
    month_str: str | None = None,
    year_str: str | None = None,
    cursor: sqlite3.Cursor | None = None,
):
    user_hour_count = {}
    query = "SELECT datetime, user_ids FROM hourly_activity"
    params = ()
    if period == "month" and month_str:
        query += " WHERE datetime LIKE ?"
        params = (month_str + "%",)
    elif period == "year" and year_str:
        query += " WHERE datetime LIKE ?"
        params = (year_str + "%",)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    for row in rows:
        user_ids = row[1].split(",")
        for user_id in user_ids:
            user_hour_count[user_id] = user_hour_count.get(user_id, 0) + 1
    df = pd.DataFrame(list(user_hour_count.items()), columns=["User ID", "Hours Active"])
    return df.sort_values(by="Hours Active", ascending=False)


@sql_kit(ACTIVITIES_DB)
def log_user_activity(user_id: int, cursor: sqlite3.Cursor):
    now = datetime.now(tz(TIMEZONE))
    date = now.strftime("%Y-%m-%d")
    hour = now.strftime("%Y-%m-%d %H:00")

    cursor.execute("SELECT user_ids FROM daily_activity WHERE date = ?", (date,))
    result = cursor.fetchone()

    if not result:
        cursor.execute(
            "INSERT INTO daily_activity (date, user_ids) VALUES (?, ?)", (date, str(user_id))
        )
    else:
        user_ids = result[0].split(",")
        if str(user_id) not in user_ids:
            user_ids.append(str(user_id))
            updated_user_ids = ",".join(user_ids)
            cursor.execute(
                "UPDATE daily_activity SET user_ids = ? WHERE date = ?", (updated_user_ids, date)
            )

    cursor.execute("SELECT user_ids FROM hourly_activity WHERE datetime = ?", (hour,))
    result = cursor.fetchone()

    if not result:
        cursor.execute(
            "INSERT INTO hourly_activity (datetime, user_ids) VALUES (?, ?)", (hour, str(user_id))
        )
    else:
        user_ids = result[0].split(",")
        if str(user_id) not in user_ids:
            user_ids.append(str(user_id))
            updated_user_ids = ",".join(user_ids)
            cursor.execute(
                "UPDATE hourly_activity SET user_ids = ? WHERE datetime = ?",
                (updated_user_ids, hour),
            )
