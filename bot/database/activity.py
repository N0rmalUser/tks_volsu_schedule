from config import ACTIVITIES_DB, USERS_DB, timezone

from datetime import datetime, timedelta

from bot.database.utils import sql_kit

import pytz

import sqlite3


@sql_kit(ACTIVITIES_DB)
def init_db_activity(cursor: sqlite3.Cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Activity_Stats (
            date TEXT,
            hour INTEGER,
            user_count INTEGER,
            PRIMARY KEY (date, hour)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Unique_Activity (
            date TEXT,
            hour INTEGER,
            user_id INTEGER,
            PRIMARY KEY (date, hour, user_id)
        );
    """)


@sql_kit(USERS_DB)
def get_last_hour_users(cursor: sqlite3.Cursor) -> list:
    """Возвращает список пользователей, которые заходили в бота в последний час"""
    one_hour_ago = datetime.now(pytz.timezone(timezone)) - timedelta(hours=1)

    cursor.execute("SELECT user_id, last_date FROM User_Info")
    all_users = cursor.fetchall()

    active_users = []
    for user_id, last_date_str in all_users:
        last_date = pytz.timezone(timezone).localize(datetime.strptime(last_date_str, '%d-%m-%Y %H:%M:%S'))
        if last_date >= one_hour_ago:
            active_users.append(user_id)
    return active_users


@sql_kit(ACTIVITIES_DB)
def update_user_activity_stats(cursor: sqlite3.Cursor):
    active_users = get_last_hour_users()
    current_datetime = datetime.now(pytz.timezone('Europe/Moscow'))
    date_str = current_datetime.strftime('%d-%m-%Y')
    current_hour = current_datetime.hour

    # Сначала обновляем таблицу уникальных пользователей
    for user_id in active_users:
        cursor.execute("""
               INSERT OR IGNORE INTO User_Unique_Activity (date, hour, user_id)
               VALUES (?, ?, ?)
           """, (date_str, current_hour, user_id))

    # Теперь подсчитываем количество уникальных пользователей для данного часа
    cursor.execute("""
           SELECT COUNT(*) FROM User_Unique_Activity
           WHERE date = ? AND hour = ?
       """, (date_str, current_hour))

    user_count = cursor.fetchone()[0]

    # Обновляем основную таблицу статистики активности пользователей
    cursor.execute("""
           INSERT INTO User_Activity_Stats (date, hour, user_count)
           VALUES (?, ?, ?)
           ON CONFLICT(date, hour) DO UPDATE SET user_count = excluded.user_count
       """, (date_str, current_hour, user_count))


@sql_kit(ACTIVITIES_DB)
def fetch_user_activity_stats(cursor: sqlite3.Cursor):
    cursor.execute("SELECT * FROM User_Activity_Stats")
    data = cursor.fetchall()
    return data



