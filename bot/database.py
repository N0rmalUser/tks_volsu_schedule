import logging

from aiogram.types import Message

from config import ACTIVITIES_DB, USERS_DB, timezone

from datetime import datetime

from bot.misc.utils import sql_kit

import sqlite3


@sql_kit(USERS_DB)
def init_db(cursor: sqlite3.Cursor):
    """Создаёт бд, если её нет"""

    cursor.execute("""
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
            banned BOOLEAN DEFAULT false,
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
            defaulte TEXT,
            FOREIGN KEY (user_id) REFERENCES User_Info(user_id)
        )
    """)


@sql_kit(USERS_DB)
def set_user_type(msg: Message, user_type: str, cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля user_type, username, fullname, start_date, если они не установлены
    :param msg:  :class:`aiogram.types.Message` Полученное сообщение
    :param user_type:  :class:`str` user call_type - student или teacher
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    user_id = msg.from_user.id
    cursor.execute("""
        SELECT start_date FROM User_Info 
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()

    cursor.execute("""
        INSERT INTO User_Info(user_id, user_type)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
        SET user_type=excluded.user_type;
        """, (user_id, user_type))

    cursor.execute("""
        INSERT INTO User_Info(user_id, username)
        VALUES(?, ?) 
        ON CONFLICT(user_id) DO UPDATE 
        SET username=excluded.username;
        """, (user_id, f"@{msg.from_user.username}"))

    cursor.execute("""
        INSERT INTO User_Info(user_id, fullname)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET fullname=excluded.fullname;
        """, (user_id, msg.from_user.full_name))

    formatted_start_date = (msg.date
                            .astimezone(pytz.timezone(timezone))
                            .strftime('%d-%m-%Y %H:%M:%S'))

    if result is None or result[0] is None:
        cursor.execute("""
            INSERT INTO User_Info(user_id, start_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET start_date=excluded.start_date;
            """, (user_id, formatted_start_date))


@sql_kit(USERS_DB)
def user_exists(user_id: int, cursor: sqlite3.Cursor) -> bool:
    """Проверяет, есть ли пользователь в базе данных"""
    cursor.execute("""
        SELECT * 
        FROM User_Info 
        WHERE user_id = ?
        """, (user_id,))
    return True if cursor.fetchone() is not None else False


@sql_kit(USERS_DB)
def set_blocked(user_id: int, block: bool, cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля blocked - заблокировал пользователь бота или нет
    :param user_id:  :class:`int` user id
    :param block:  :class:`bool` block True или False
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    cursor.execute("""
            INSERT INTO User_Info(user_id, blocked)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET blocked=excluded.blocked;
            """, (user_id, block))


@sql_kit(USERS_DB)
def get_blocked(user_id: int, cursor: sqlite3.Cursor) -> bool:
    """
    Возвращает значение поля blocked - заблокировал пользователь бота или нет
    :param user_id:  :class:`int` user id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`bool` block True или False
    """
    cursor.execute("""
        SELECT blocked FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return bool(cursor.fetchone())


@sql_kit(USERS_DB)
def set_banned(user_id: int, ban: bool, cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля blocked - заблокировал пользователь бота или нет
    :param user_id:  :class:`int` user id
    :param ban:  :class:`bool` block True или False
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    cursor.execute("""
            INSERT INTO User_Info(user_id, banned)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET banned=excluded.banned;
            """, (user_id, ban))


@sql_kit(USERS_DB)
def get_banned(user_id: int, cursor: sqlite3.Cursor) -> bool:
    """
    Возвращает значение поля blocked - заблокировал пользователь бота или нет
    :param user_id:  :class:`int` user id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`bool` ban True или False
    """
    try:
        cursor.execute("""
            SELECT banned FROM User_Info
            WHERE user_id = ?
            """, (user_id,))
    except Exception:
        pass
    result = cursor.fetchone()
    return bool(result[0]) if result is not None else False


@sql_kit(USERS_DB)
def set_tracking(user_id: int, tracking: bool, cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля tracking - отслеживание пользователя
    :param user_id:  :class:`int` user id
    :param tracking:  :class:`bool` tracking True или False
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    cursor.execute("""
            INSERT INTO Temp_Data(user_id, tracking)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET tracking=excluded.tracking;
            """, (user_id, tracking))


@sql_kit(USERS_DB)
def get_tracking(user_id: int, cursor: sqlite3.Cursor) -> bool:
    """
    Возвращает значение поля tracking - отслеживание пользователя
    :param user_id:  :class:`int` user id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`bool` tracking True или False
    """
    cursor.execute("""
        SELECT tracking FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    try:
        return bool(cursor.fetchone()[0])
    except Exception:
        return False


@sql_kit(USERS_DB)
def get_user_type(user_id: int, cursor: sqlite3.Cursor) -> str:
    """
    Возвращает значение поля user_type - student или teacher
    :param user_id:  :class:`int` user id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` user call_type - student или teacher
    """
    cursor.execute("""
        SELECT user_type FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return cursor.fetchone()[0]


@sql_kit(USERS_DB)
def set_last_date(msg: Message, cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля last_date - дата последнего сообщения от пользователя
    :param msg:  :class:`aiogram.types.Message` Полученное сообщение
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    formatted_last_date = (msg.date
                           .astimezone(pytz.timezone(timezone))
                           .strftime('%d-%m-%Y %H:%M:%S'))
    cursor.execute("""
        INSERT INTO User_Info(user_id, last_date)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET last_date=excluded.last_date;
        """, (msg.from_user.id, formatted_last_date))


@sql_kit(USERS_DB)
def set_inviter(user_id: int, inviter_id: int, cursor: sqlite3.Cursor):
    """
    Устанавливает значение для поля inviter_id - id пригласившего пользователя
    :param user_id:  :class:`int` user id
    :param inviter_id:  :class:`int` id пригласившего пользователя
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    cursor.execute("""
        SELECT inviter_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("""
            INSERT INTO User_Info(user_id, inviter_id) 
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET inviter_id=excluded.inviter_id;
            """, (user_id, inviter_id))


@sql_kit(USERS_DB)
def get_inviter(user_id: int, cursor: sqlite3.Cursor) -> int:
    """
    Возвращает значение поля inviter_id - id пригласившего пользователя
    :param user_id:  :class:`int` user id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`int` id пригласившего пользователя
    """
    cursor.execute("""
        SELECT inviter_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return cursor.fetchone()[0]


@sql_kit(USERS_DB)
def get_teacher(user_id: int, cursor: sqlite3.Cursor) -> str:
    """
    Возвращает значение поля teacher_name - имя преподавателя
    :param user_id:  :class:`int` user id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` Имя преподавателя
    """
    cursor.execute("""
        SELECT teacher_name FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(USERS_DB)
def set_teacher(user_id: int, teacher_name: str, cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля teacher_name - имя преподавателя
    :param user_id:  :class:`int` user id
    :param teacher_name:  :class:`str` Имя преподавателя
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, teacher_name)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET teacher_name=excluded.teacher_name;
        """, (user_id, teacher_name))


@sql_kit(USERS_DB)
def get_group(user_id: int, cursor: sqlite3.Cursor) -> str:
    """
    Возвращает значение поля group_name - название группы
    :param user_id:  :class:`int` user id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` Название группы
    """
    cursor.execute("""
        SELECT group_name FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(USERS_DB)
def set_group(user_id: int, group_name: str, cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля group_name - название группы
    :param user_id:  :class:`int` user id
    :param group_name:  :class:`str` Название группы
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, group_name)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET group_name=excluded.group_name;
        """, (user_id, group_name))


@sql_kit(USERS_DB)
def get_topic_id(user_id: int, cursor: sqlite3.Cursor) -> int:
    """
    Возвращает значение поля topic_id - id топика пользователя
    :param user_id:  :class:`int` user id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`int` topic id - id топика пользователя
    """
    cursor.execute("""
        SELECT topic_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else False


@sql_kit(USERS_DB)
def get_user_id(topic_id: int, cursor: sqlite3.Cursor) -> int:
    """
    Возвращает значение поля user_id - id пользователя
    :param topic_id:  :class:`int` topic id
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`int` user id - id пользователя в telegram
    """
    cursor.execute("""
        SELECT user_id FROM User_Info
        WHERE topic_id = ?
        """, (topic_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(USERS_DB)
def set_topic_id(user_id: int, topic_id: int, cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля topic_id - id топика пользователя
    :param user_id:  :class:`int` user id - id пользователя в telegram
    :param topic_id:  :class:`int` topic id - id топика пользователя
    :param cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    cursor.execute("""
        INSERT INTO User_Info(user_id, topic_id)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET topic_id=excluded.topic_id;
        """, (user_id, topic_id))


@sql_kit(USERS_DB)
def delete_topic_id(user_id, cursor: sqlite3.Cursor):
    cursor.execute("UPDATE User_info SET topic_id = NULL WHERE user_id = ?;", (user_id,))


@sql_kit(USERS_DB)
def get_week(user_id: int, cursor: sqlite3.Cursor) -> int:
    """Возвращает значение поля week. 1 - 'Числитель', 2 - 'Знаменатель'"""
    cursor.execute("""
        SELECT week FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return int(result[0]) if result else None


@sql_kit(USERS_DB)
def set_week(user_id: int, week: int, cursor: sqlite3.Cursor) -> None:
    """Устанавливает значение поля week. 1 - 'Числитель', 2 - 'Знаменатель'"""
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, week)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET week=excluded.week;
        """, (user_id, week))


@sql_kit(USERS_DB)
def get_day(user_id: int, cursor: sqlite3.Cursor) -> int:
    """Устанавливает значение поля day. 1 - 'Понедельник', 2 - 'Вторник' ... 6 - 'Суббота'"""
    cursor.execute("""
        SELECT day FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(USERS_DB)
def set_day(user_id: int, day: int, cursor: sqlite3.Cursor) -> None:
    """Возвращает значение поля day. 1 - 'Понедельник', 2 - 'Вторник' ... 6 - 'Суббота'"""
    cursor.execute("""
        INSERT INTO Temp_Data(user_id, day)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET day=excluded.day;
        """, (user_id, day))


@sql_kit(USERS_DB)
def set_default(user_id: int, default: str, cursor: sqlite3.Cursor):
    cursor.execute("""
        INSERT INTO User_Info(user_id, defaulte)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET defaulte=excluded.defaulte;
        """, (user_id, default))


@sql_kit(USERS_DB)
def get_default(user_id: int, cursor: sqlite3.Cursor):
    cursor.execute("""
        SELECT defaulte FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


@sql_kit(USERS_DB)
def get_user_info(user_id: int, cursor: sqlite3.Cursor):
    """Возвращает информацию о пользователе, подготовленную к отправке админу"""
    cursor.execute("""
        SELECT * 
        FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    data = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    temp = cursor.fetchall()[0]
    print(data)
    print(temp)
    print(temp[1])
    last_date = datetime.strptime(data[6], '%d-%m-%Y %H:%M:%S').date()
    days_until = (last_date - datetime.today().date()).days
    return f"""
Информация о пользователе:
`user_type:``  ``{data[1]}`
`username:``   ``{data[2]}`
`fullname:``   ``{data[3]}`
`start_date:`` ``{data[5]}`
`last_date:``  ``{data[6]}`
`            `{-days_until} дней назад
`inviter_id:`` ``{data[7]}`
`blocked``     ``{bool(data[8])}`
`banned``      ``{bool(data[9])}`

`tracking``     ``{bool(temp[1])}`
`teacher``      ``{temp[4]}`
`group``        ``{str(temp[5]).replace("-", "")}`
"""


@sql_kit(USERS_DB)
def get_all_user_ids(cursor: sqlite3.Cursor) -> list:
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
    # Подсчёт количества пользователей, когда-либо заходивших в бота
    cursor.execute("SELECT COUNT(*) FROM User_Info")
    users_count = cursor.fetchone()[0]

    # Подсчет количества пользователей с last_date не старше одной недели
    cursor.execute("SELECT last_date FROM User_Info")
    users = cursor.fetchall()
    month_users_count, week_users_count, today_users_count = 0, 0, 0
    today = datetime.today().date()
    for (last_date_str,) in users:
        last_date = datetime.strptime(last_date_str, '%d-%m-%Y %H:%M:%S').date()
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

    result = (f"Пользователей: {users_count}\n\n"
              f"Из них:\n"
              f"Преподов {teachers}\n"
              f"Студентов {int(users_count) - int(teachers)}\n\n"
              f"Активных:\n"
              f"За месяц - {month_users_count}\n"
              f"За неделю - {week_users_count}\n"
              f"За день - {today_users_count}\n"
              f"Заблокировали бота: {blocked_count}\n"
              f"Забанено: {banned_count}")
    return result


async def broadcast_message(bot, text: str) -> None:
    """
    Отправляет сообщение всем пользователям, которые не заблокировали бота
    :param bot:  :class:`aiogram.Bot` экземпляр бота
    :param text:  :class:`str` Текст сообщения
    """
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        if not get_blocked(user_id):
            try:
                await bot.send_message(user_id, text)
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")


async def tracking_manage(tracking: bool) -> None:
    """
    Включает или выключает отслеживание для всех пользователей
    :param tracking:  :class:`bool` True или False
    """
    for user_id in get_all_user_ids():
        set_tracking(user_id, tracking)


async def get_tracked_users() -> list:
    """
    Возвращает список отслеживаемых пользователей
    :return:  :class:`list` Список отслеживаемых пользователей
    """
    user_ids = get_all_user_ids()
    tracked_users = []
    for user_id in user_ids:
        if get_tracking(user_id):
            tracked_users.append(f'`{user_id}`')
    return tracked_users


def set_today_date(user_id: int) -> None:
    """Устанавливает день и неделю в зависимости от текущей даты"""
    day = int(f"{datetime.now(pytz.timezone(timezone)).weekday() + 1}")
    week = 2 if datetime.now(pytz.timezone(timezone)).isocalendar()[1] % 2 == 0 else 1
    if day == 7:
        set_day(user_id, 1)
        set_week(user_id, week + 1 if week == 1 else week - 1)
    else:
        set_day(user_id, day)
        set_week(user_id, week)
