from aiogram.types import Message

from data.config import DB_PATH
from data import config

from datetime import datetime

from functools import wraps

import json

import sqlite3


def sql_kit(db=":memory:"):
    """
    Decorator for working with database
    :param db:  path to database
    :return:  function result
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db)
            try:
                result = func(*args, **kwargs, _cursor=conn.cursor())
                conn.commit()
                return result
            finally:
                conn.close()

        return wrapper

    return decorator


@sql_kit(DB_PATH)
def init_db(_cursor):
    """
    Create tables if not exists
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Info (
            user_id INTEGER PRIMARY KEY,
            user_type TEXT DEFAULT student,
            username TEXT,
            fullname TEXT,
            topic_id INTEGER,
            start_date TEXT,
            last_date TEXT,
            inviter_id INTEGER,
            blocked BOOLEAN DEFAULT false,
            FOREIGN KEY (inviter_id) REFERENCES User_Info(user_id)
        )
    """)

    _cursor.execute("""
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
def set_blocked(user_id: int, block: bool, _cursor=None):
    _cursor.execute("""
            INSERT INTO User_Info(user_id, blocked)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET blocked=excluded.blocked;
            """, (user_id, block))


@sql_kit(DB_PATH)
def get_blocked(user_id: int, _cursor=None) -> bool:
    _cursor.execute("""
        SELECT blocked FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return bool(_cursor.fetchone())


@sql_kit(DB_PATH)
def set_tracking(user_id: int, tracking: bool, _cursor=None):
    """
    Set tracking param for user
    :param user_id:  :class:`aiogram.types.Message`
    :param tracking:  :class:`bool` tracking True or False
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
            INSERT INTO Temp_Data(user_id, tracking)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET tracking=excluded.tracking;
            """, (user_id, tracking))


@sql_kit(DB_PATH)
def get_tracking(user_id: int, _cursor=None) -> bool:
    """
    Get tracking param for user
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`bool` tracking - True or False
    """
    _cursor.execute("""
        SELECT tracking FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    try:
        return bool(_cursor.fetchone()[0])
    except Exception:
        return False


@sql_kit(DB_PATH)
def get_user_type(user_id: int, _cursor=None) -> str:
    """
    Get user type - student or teacher
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`str` user type - student or teacher
    """
    _cursor.execute("""
        SELECT user_type FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return _cursor.fetchone()[0]


@sql_kit(DB_PATH)
def set_user_type(msg: Message, user_type: str, _cursor=None):
    """
    Set user type, username, fullname, start_date for user
    :param msg:  :class:`aiogram.types.Message`
    :param user_type:  :class:`str` user type - student or teacher
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`str` user type - student or teacher
    """
    _cursor.execute("""
        SELECT start_date FROM User_Info 
        WHERE user_id = ?
        """, (msg.from_user.id,))
    result = _cursor.fetchone()

    _cursor.execute("""
        INSERT INTO User_Info(user_id, user_type)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
        SET user_type=excluded.user_type;
        """, (msg.from_user.id, user_type))

    _cursor.execute("""
        INSERT INTO User_Info(user_id, username)
        VALUES(?, ?) 
        ON CONFLICT(user_id) DO UPDATE 
        SET username=excluded.username;
        """, (msg.from_user.id, f"@{msg.from_user.username}"))

    _cursor.execute("""
        INSERT INTO User_Info(user_id, fullname)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET fullname=excluded.fullname;
        """, (msg.from_user.id, msg.from_user.full_name))

    if result is None or result[0] is None:
        _cursor.execute("""
            INSERT INTO User_Info(user_id, start_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET start_date=excluded.start_date;
            """, (msg.from_user.id, f"{msg.date.strftime('%d-%m-%Y')} "
                                    f"{msg.date.strftime('%H:%M:%S')}"))


@sql_kit(DB_PATH)
def set_last_date(msg: Message, _cursor=None):
    """
    Set last_date when user used bot
    :param msg:  :class:`aiogram.types.Message`
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
        INSERT INTO User_Info(user_id, last_date)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET last_date=excluded.last_date;
        """, (msg.from_user.id, f"{msg.date.strftime('%d-%m-%Y')} "
                                f"{msg.date.strftime('%H:%M:%S')}"))


@sql_kit(DB_PATH)
def set_inviter(user_id: int, inviter_id: int, _cursor=None):
    """
    Set user`s inviter_id
    :param user_id:  :class:`int` user id
    :param inviter_id:  :class:`int` inviter id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
        SELECT inviter_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    if result is None:
        _cursor.execute("""
            INSERT INTO User_Info(user_id, inviter_id) 
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET inviter_id=excluded.inviter_id;
            """, (user_id, inviter_id))


@sql_kit(DB_PATH)
def get_inviter(user_id: int, _cursor=None) -> int:
    """
    Get user`s inviter_id
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`int` inviter id
    """
    _cursor.execute("""
        SELECT inviter_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return _cursor.fetchone()[0]


@sql_kit(DB_PATH)
def get_teacher(user_id: int, _cursor=None) -> str:
    """
    Get teacher name
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`str` teacher name
    """
    _cursor.execute("""
        SELECT teacher_name FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_teacher(user_id: int, teacher_name: str, _cursor=None) -> None:
    """
    Set teacher name
    :param user_id:  :class:`int` user id
    :param teacher_name:  :class:`str` teacher name
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, teacher_name)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET teacher_name=excluded.teacher_name;
        """, (user_id, teacher_name))


@sql_kit(DB_PATH)
def get_group(user_id: int, _cursor=None) -> str:
    """
    Get group name
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`str` group name
    """
    _cursor.execute("""
        SELECT group_name FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_group(user_id: int, group_name: str, _cursor=None):
    """
    Set group name
    :param user_id:  :class:`int` user id
    :param group_name:  :class:`str` group name
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, group_name)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET group_name=excluded.group_name;
        """, (user_id, group_name))


@sql_kit(DB_PATH)
def get_topic_id(user_id: int, _cursor=None) -> int:
    """
    Get topic id
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`int` topic id
    """
    _cursor.execute("""
        SELECT topic_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else False


@sql_kit(DB_PATH)
def get_user_id(topic_id: int, _cursor=None) -> int:
    """
    Get user id
    :param topic_id:  :class:`int` topic id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`int` user id
    """
    _cursor.execute("""
        SELECT user_id FROM User_Info
        WHERE topic_id = ?
        """, (topic_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_topic_id(user_id: int, topic_id: int, _cursor=None):
    """
    Set topic id
    :param user_id:  :class:`int` user id
    :param topic_id:  :class:`int` topic id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
        INSERT INTO User_Info(user_id, topic_id)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET topic_id=excluded.topic_id;
        """, (user_id, topic_id))


@sql_kit(DB_PATH)
def get_week(user_id: int, _cursor=None) -> int:
    """
    Get week. 1 - "Числитель", 2 - "Знаменатель"
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`int` week
    """
    _cursor.execute("""
        SELECT week FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return int(result[0]) if result else None


@sql_kit(DB_PATH)
def set_week(user_id: int, week: int, _cursor=None) -> None:
    """
    Set week. 1 - "Числитель", 2 - "Знаменатель"
    :param user_id:  :class:`int` user id
    :param week:  :class:`int` week
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, week)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET week=excluded.week;
        """, (user_id, week))


@sql_kit(DB_PATH)
def get_day(user_id: int, _cursor=None) -> int:
    """
    Get day. 1 - "Понедельник", 2 - "Вторник" ... 6 - "Суббота"
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`int` day
    """
    _cursor.execute("""
        SELECT day FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_day(user_id: int, day: int, _cursor=None) -> None:
    """
    Set day. 1 - "Понедельник", 2 - "Вторник" ... 6 - "Суббота"
    :param user_id:  :class:`int` user id
    :param day:  :class:`int` day
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  None
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, day)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET day=excluded.day;
        """, (user_id, day))


@sql_kit(DB_PATH)
def get_room(user_id: int, _cursor=None) -> str:
    """
    Get room
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`str` room
    """
    _cursor.execute("""SELECT room FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_room(user_id: int, room: str, _cursor=None):
    """
    Set room
    :param user_id:  :class:`int` user id
    :param room:  :class:`str` room
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return: None
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, room)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET room=excluded.room;
        """, (user_id, room))


@sql_kit(DB_PATH)
def get_user_info(user_id, _cursor):
    _cursor.execute("""
        SELECT * FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    data = _cursor.fetchone()
    return f"""
Информация о пользователе:
`user_id:``    ``{data[0]}`
`user_type:``  ``{data[1]}`
`username:``   ``{data[2]}`
`fullname:``   ``{data[3]}`
`topic_id:``   ``{data[4]}`
`start_date:`` ``{data[5]}`
`last_date:``  ``{data[6]}`
`inviter_id:`` ``{data[7]}`
"""


@sql_kit(DB_PATH)
def get_all_user_ids(_cursor) -> list:
    """
    Get all user ids
    :param _cursor:  :class:`sqlite3.Cursor` Internal cursor for working with database
    :return:  :class:`list` user id`s
    """
    _cursor.execute("SELECT user_id FROM User_Info")
    return [row[0] for row in _cursor.fetchall()]


async def broadcast_message(bot, text) -> None:
    """
    Send message to all users
    :param bot:  :class:`aiogram.Bot`
    :param text:  :class:`str` message text
    :return:  None
    """
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        if get_blocked(user_id):
            try:
                await bot.send_message(user_id, text)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")


async def tracking_manage(tracking: bool) -> None:
    """
    Manage tracking param
    :param tracking:  :class:`bool` tracking True or False
    :return:  None
    """
    for user_id in get_all_user_ids():
        set_tracking(user_id, tracking)


async def get_tracked_users() -> list:
    """
    Get tracked users
    :return:  :class:`list` user id`s
    """
    user_ids = get_all_user_ids()
    tracked_users = []
    for user_id in user_ids:
        if get_tracking(user_id):
            tracked_users.append(user_id)
    return tracked_users


def open_schedule_file():
    """
    Open files with schedule
    :return:  None
    """
    with open(config.SCHEDULE_PATH, 'r', encoding='utf-8') as file:
        config.schedule = json.load(file)


def set_today_date(user_id: int) -> None:
    """
    Set today date
    :param user_id:  :class:`int` user id
    :return:  None
    """
    day = int(f"{datetime.now().weekday() + 1}")
    week = 2 if datetime.now().isocalendar()[1] % 2 == 0 else 1
    if day == 7:
        set_day(user_id, 1)
        set_week(user_id, week+1 if week == 1 else week-1)
    else:
        set_day(user_id, day)
        set_week(user_id, week)
