from aiogram.types import Message

from data.config import DB_PATH
from data import config

from datetime import datetime

from functools import wraps

import json

import sqlite3


def sql_kit(db=":memory:"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db)
            try:
                result = func(*args,  **kwargs, cursor=conn.cursor())
                conn.commit()
                return result
            finally:
                conn.close()
        return wrapper
    return decorator


@sql_kit(DB_PATH)
def init_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Info (
            user_id INTEGER PRIMARY KEY,
            user_type TEXT DEFAULT student,
            username TEXT,
            fullname TEXT,
            topic_id INTEGER,
            full_name TEXT,
            start_date TEXT,
            last_date TEXT,
            inviter_id INTEGER,
            FOREIGN KEY (inviter_id) REFERENCES User_Info(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Temp_Data (
            user_id INTEGER PRIMARY KEY,
            tracking BOOLEAN DEFAULT false,
            week INTEGER,
            day INTEGER,
            teacher_name TEXT,
            group_name TEXT,
            room TEXT,
            FOREIGN KEY (user_id) REFERENCES User_Info(user_id)
        )
    """)


@sql_kit(DB_PATH)
def set_tracking(msg: Message, tracking: bool, cursor=None):
    cursor.execute("""
            INSERT INTO Temp_Data(user_id, tracking)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET tracking=excluded.tracking;
            """, (msg.from_user.id, tracking))


@sql_kit(DB_PATH)
def get_tracking(user_id: int, cursor=None) -> bool:
    cursor.execute("""
        SELECT tracking FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    return bool(cursor.fetchone()[0])


@sql_kit(DB_PATH)
def get_user_type(user_id: int, cursor=None) -> str:
    cursor.execute("""
        SELECT user_type FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return cursor.fetchone()[0]


@sql_kit(DB_PATH)
def set_user_type(msg: Message, user_type: str, cursor=None):
    cursor.execute("""
        SELECT start_date FROM User_Info 
        WHERE user_id = ?
        """, (msg.from_user.id,))
    result = cursor.fetchone()

    cursor.execute("""
        INSERT INTO User_Info(user_id, user_type)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
        SET user_type=excluded.user_type;
        """, (msg.from_user.id, user_type))

    cursor.execute("""
        INSERT INTO User_Info(user_id, username)
        VALUES(?, ?) 
        ON CONFLICT(user_id) DO UPDATE 
        SET username=excluded.username;
        """, (msg.from_user.id, f"@{msg.from_user.username}"))

    cursor.execute("""
        INSERT INTO User_Info(user_id, fullname)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET fullname=excluded.fullname;
        """, (msg.from_user.id, msg.from_user.full_name))

    if result is None or result[0] is None:
        cursor.execute("""
            INSERT INTO User_Info(user_id, start_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET start_date=excluded.start_date;
            """, (msg.from_user.id, f"{msg.date.strftime('%d-%m-%Y')}"
                                    f"{msg.date.strftime('%H:%M:%S')}"))


@sql_kit(DB_PATH)
def set_last_date(msg: Message, cursor=None):
    cursor.execute("""
        INSERT INTO User_Info(user_id, last_date)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET last_date=excluded.last_date;
        """, (msg.from_user.id, f"{msg.date.strftime('%d-%m-%Y')}"
                                f"{msg.date.strftime('%H:%M:%S')}"))


@sql_kit(DB_PATH)
def set_inviter(user_id: int, inviter_id: int, cursor=None):
    cursor.execute("""
        SELECT inviter_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    if result[0] is None:
        cursor.execute("""
            INSERT INTO User_Info(user_id, inviter_id) 
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET inviter_id=excluded.inviter_id;
            """, (user_id, inviter_id))


@sql_kit(DB_PATH)
def get_inviter(user_id: int, cursor=None):
    cursor.execute("""
        SELECT inviter_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return cursor.fetchone()[0]


@sql_kit(DB_PATH)
def get_teacher(user_id: int, cursor=None):
    cursor.execute("""
        SELECT teacher_name FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_teacher(user_id: int, teacher_name: str, cursor=None):
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, teacher_name)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET teacher_name=excluded.teacher_name;
        """, (user_id, teacher_name))


@sql_kit(DB_PATH)
def get_group(user_id: int, cursor=None):
    cursor.execute("""
        SELECT group_name FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_group(user_id: int, group_name: str, cursor=None):
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, group_name)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET group_name=excluded.group_name;
        """, (user_id, group_name))


@sql_kit(DB_PATH)
def get_topic_id(user_id: int, cursor=None):
    cursor.execute("""
        SELECT topic_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else False


@sql_kit(DB_PATH)
def get_user_id(topic_id: int, cursor=None):
    cursor.execute("""
        SELECT user_id FROM User_Info
        WHERE topic_id = ?
        """, (topic_id,))
    result = cursor.fetchone()
    return result[0] if result else False


@sql_kit(DB_PATH)
def set_topic_id(user_id: int, topic_id: int, cursor=None):
    cursor.execute("""
        INSERT INTO User_Info(user_id, topic_id)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET topic_id=excluded.topic_id;
        """, (user_id, topic_id))


@sql_kit(DB_PATH)
def get_week(user_id: int, cursor=None):
    cursor.execute("""
        SELECT week FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return int(result[0]) if result else None


@sql_kit(DB_PATH)
def set_week(user_id: int, week: int, cursor=None):
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, week)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET week=excluded.week;
        """, (user_id, week))


@sql_kit(DB_PATH)
def get_day(user_id: int, cursor=None):
    cursor.execute("""
        SELECT day FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_day(user_id: int, day: int, cursor=None):
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, day)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET day=excluded.day;
        """, (user_id, day))


@sql_kit(DB_PATH)
def get_room(user_id: int, cursor=None):
    cursor.execute("""SELECT room FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_room(user_id: int, room: str, cursor=None):
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, room)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET room=excluded.room;
        """, (user_id, room))


@sql_kit(DB_PATH)
def get_all_user_ids(cursor):
    cursor.execute("SELECT user_id FROM User_Info")
    return [row[0] for row in cursor.fetchall()]


async def broadcast_message(bot, text):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")


def open_files():
    with open(config.SCHEDULE, 'r', encoding='utf-8') as file:
        config.schedule = json.load(file)


def set_today_date(user_id: int):
    set_day(user_id, int(f"{datetime.now().weekday() + 1}"))
    set_week(user_id, 2 if datetime.now().isocalendar()[1] % 2 == 0 else 1)
