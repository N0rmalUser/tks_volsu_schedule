import logging

from config import ACTIVITIES_DB, USERS_DB, timezone

from datetime import datetime, timedelta

from bot.database.utils import sql_kit

import pytz

import sqlite3


@sql_kit(USERS_DB)
def get_last_hour_users(cursor: sqlite3.Cursor) -> list:
    """Возвращает список пользователей, которые были активны в течение предыдущего часа."""

    start_of_last_hour = datetime.now(pytz.timezone(timezone)).replace(minute=0, second=0, microsecond=0)- timedelta(hours=1)
    end_of_last_hour = start_of_last_hour + timedelta(hours=1)

    cursor.execute("""
        SELECT user_id FROM User_Info
        WHERE last_date >= ? AND last_date < ?
    """, (start_of_last_hour.strftime('%d-%m-%Y %H:%M:%S'), end_of_last_hour.strftime('%d-%m-%Y %H:%M:%S')))

    return [row[0] for row in cursor.fetchall()]


@sql_kit(ACTIVITIES_DB)
def update_user_activity_stats(cursor: sqlite3.Cursor):
    """Обновляет статистику активности пользователей за последний час. Удаляет данные из вспомогательной таблицы User_Unique_Activity, которые устарели на 2 часа."""

    two_hours_ago = datetime.now(pytz.timezone(timezone)).replace(minute=0, second=0, microsecond=0) - timedelta(hours=2)

    cursor.execute("""
        DELETE FROM User_Unique_Activity
        WHERE date < ? OR (date = ? AND hour < ?)
        """, (two_hours_ago.strftime('%d-%m-%Y'), two_hours_ago.strftime('%d-%m-%Y'), two_hours_ago.hour))

    active_users = get_last_hour_users()
    current_datetime = datetime.now(pytz.timezone('Europe/Moscow'))
    date_str = current_datetime.strftime('%d-%m-%Y')
    current_hour = current_datetime.hour

    cursor.executemany("""
        INSERT OR IGNORE INTO User_Unique_Activity (date, hour, user_id)
        VALUES (?, ?, ?)
    """, [(date_str, current_hour, user_id) for user_id in active_users])

    cursor.execute("""
       SELECT COUNT(*) FROM User_Unique_Activity
       WHERE date = ? AND hour = ?
       """, (date_str, current_hour))

    user_count = cursor.fetchone()[0]

    cursor.execute("""
       INSERT INTO User_Activity_Stats (date, hour, user_count)
       VALUES (?, ?, ?)
       ON CONFLICT(date, hour) DO UPDATE SET user_count = excluded.user_count
       """, (date_str, current_hour, user_count))

    logging.info(f"Статистика активности пользователей за {current_datetime.strftime('%d-%m-%Y %H:%M')} обновлена")


@sql_kit(ACTIVITIES_DB)
def fetch_user_activity_stats(cursor: sqlite3.Cursor):
    """Возвращает статистику активности пользователей за последние 24 часа."""

    cursor.execute("SELECT * FROM User_Activity_Stats")
    data = cursor.fetchall()
    return data



