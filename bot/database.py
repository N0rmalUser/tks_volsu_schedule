from aiogram.types import Message

from config import DB_PATH

from datetime import datetime, timedelta

from functools import wraps

import sqlite3


def sql_kit(db=":memory:"):
    """
    Декоратор для работы с базой данных. Он открывает соединение с базой данных, выполняет функцию и закрывает соединение.
    :param db:  путь к базе данных
    :return:  результат выполнения функции
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
def init_db(_cursor: sqlite3.Cursor):
    """Создаёт бд, если её нет"""

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
            banned BOOLEAN DEFAULT false,
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
def set_user_type(msg: Message, user_type: str, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля user_type, username, fullname, start_date, если они не установлены
    :param msg:  :class:`aiogram.types.Message` Полученное сообщение
    :param user_type:  :class:`str` user call_type - student или teacher
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    user_id = msg.from_user.id
    _cursor.execute("""
        SELECT start_date FROM User_Info 
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()

    _cursor.execute("""
        INSERT INTO User_Info(user_id, user_type)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
        SET user_type=excluded.user_type;
        """, (user_id, user_type))

    _cursor.execute("""
        INSERT INTO User_Info(user_id, username)
        VALUES(?, ?) 
        ON CONFLICT(user_id) DO UPDATE 
        SET username=excluded.username;
        """, (user_id, f"@{msg.from_user.username}"))

    _cursor.execute("""
        INSERT INTO User_Info(user_id, fullname)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET fullname=excluded.fullname;
        """, (user_id, msg.from_user.full_name))

    if result is None or result[0] is None:
        _cursor.execute("""
            INSERT INTO User_Info(user_id, start_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET start_date=excluded.start_date;
            """, (user_id, f"{msg.date.strftime('%d-%m-%Y')} "
                           f"{msg.date.strftime('%H:%M:%S')}"))


@sql_kit(DB_PATH)
def user_exists(user_id: int, _cursor: sqlite3.Cursor) -> bool:
    _cursor.execute("""
        SELECT * 
        FROM User_Info 
        WHERE user_id = ?
        """, (user_id,))
    return True if _cursor.fetchone() is not None else False


@sql_kit(DB_PATH)
def set_blocked(user_id: int, block: bool, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля blocked - заблокировал пользователь бота или нет
    :param user_id:  :class:`int` user id
    :param block:  :class:`bool` block True или False
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
            INSERT INTO User_Info(user_id, blocked)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET blocked=excluded.blocked;
            """, (user_id, block))


@sql_kit(DB_PATH)
def get_blocked(user_id: int, _cursor: sqlite3.Cursor) -> bool:
    """
    Возвращает значение поля blocked - заблокировал пользователь бота или нет
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`bool` block True или False
    """
    _cursor.execute("""
        SELECT blocked FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return bool(_cursor.fetchone())


@sql_kit(DB_PATH)
def set_banned(user_id: int, ban: bool, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля blocked - заблокировал пользователь бота или нет
    :param user_id:  :class:`int` user id
    :param ban:  :class:`bool` block True или False
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
            INSERT INTO User_Info(user_id, banned)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET banned=excluded.banned;
            """, (user_id, ban))


@sql_kit(DB_PATH)
def get_banned(user_id: int, _cursor: sqlite3.Cursor) -> bool:
    """
    Возвращает значение поля blocked - заблокировал пользователь бота или нет
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`bool` ban True или False
    """
    try:
        _cursor.execute("""
            SELECT banned FROM User_Info
            WHERE user_id = ?
            """, (user_id,))
    except Exception:
        pass
    result = _cursor.fetchone()
    return bool(result[0]) if result is not None else False


@sql_kit(DB_PATH)
def set_tracking(user_id: int, tracking: bool, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля tracking - отслеживание пользователя
    :param user_id:  :class:`int` user id
    :param tracking:  :class:`bool` tracking True или False
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
            INSERT INTO Temp_Data(user_id, tracking)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET tracking=excluded.tracking;
            """, (user_id, tracking))


@sql_kit(DB_PATH)
def get_tracking(user_id: int, _cursor: sqlite3.Cursor) -> bool:
    """
    Возвращает значение поля tracking - отслеживание пользователя
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`bool` tracking True или False
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
def get_user_type(user_id: int, _cursor: sqlite3.Cursor) -> str:
    """
    Возвращает значение поля user_type - student или teacher
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` user call_type - student или teacher
    """
    _cursor.execute("""
        SELECT user_type FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return _cursor.fetchone()[0]


@sql_kit(DB_PATH)
def set_last_date(msg: Message, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля last_date - дата последнего сообщения от пользователя
    :param msg:  :class:`aiogram.types.Message` Полученное сообщение
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
        INSERT INTO User_Info(user_id, last_date)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET last_date=excluded.last_date;
        """, (msg.from_user.id, f"{msg.date.strftime('%d-%m-%Y')} "
                                f"{msg.date.strftime('%H:%M:%S')}"))


@sql_kit(DB_PATH)
def set_inviter(user_id: int, inviter_id: int, _cursor: sqlite3.Cursor):
    """
    Устанавливает значение для поля inviter_id - id пригласившего пользователя
    :param user_id:  :class:`int` user id
    :param inviter_id:  :class:`int` id пригласившего пользователя
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
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
def get_inviter(user_id: int, _cursor: sqlite3.Cursor) -> int:
    """
    Возвращает значение поля inviter_id - id пригласившего пользователя
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`int` id пригласившего пользователя
    """
    _cursor.execute("""
        SELECT inviter_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    return _cursor.fetchone()[0]


@sql_kit(DB_PATH)
def get_teacher(user_id: int, _cursor: sqlite3.Cursor) -> str:
    """
    Возвращает значение поля teacher_name - имя преподавателя
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` Имя преподавателя
    """
    _cursor.execute("""
        SELECT teacher_name FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_teacher(user_id: int, teacher_name: str, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля teacher_name - имя преподавателя
    :param user_id:  :class:`int` user id
    :param teacher_name:  :class:`str` Имя преподавателя
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, teacher_name)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET teacher_name=excluded.teacher_name;
        """, (user_id, teacher_name))


@sql_kit(DB_PATH)
def get_group(user_id: int, _cursor: sqlite3.Cursor) -> str:
    """
    Возвращает значение поля group_name - название группы
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` Название группы
    """
    _cursor.execute("""
        SELECT group_name FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_group(user_id: int, group_name: str, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля group_name - название группы
    :param user_id:  :class:`int` user id
    :param group_name:  :class:`str` Название группы
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, group_name)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET group_name=excluded.group_name;
        """, (user_id, group_name))


@sql_kit(DB_PATH)
def get_topic_id(user_id: int, _cursor: sqlite3.Cursor) -> int:
    """
    Возвращает значение поля topic_id - id топика пользователя
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`int` topic id - id топика пользователя
    """
    _cursor.execute("""
        SELECT topic_id FROM User_Info
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else False


@sql_kit(DB_PATH)
def get_user_id(topic_id: int, _cursor: sqlite3.Cursor) -> int:
    """
    Возвращает значение поля user_id - id пользователя
    :param topic_id:  :class:`int` topic id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`int` user id - id пользователя в telegram
    """
    _cursor.execute("""
        SELECT user_id FROM User_Info
        WHERE topic_id = ?
        """, (topic_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_topic_id(user_id: int, topic_id: int, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение для поля topic_id - id топика пользователя
    :param user_id:  :class:`int` user id - id пользователя в telegram
    :param topic_id:  :class:`int` topic id - id топика пользователя
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
        INSERT INTO User_Info(user_id, topic_id)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET topic_id=excluded.topic_id;
        """, (user_id, topic_id))


@sql_kit(DB_PATH)
def delete_topic_id(user_id, _cursor: sqlite3.Cursor):
    _cursor.execute("UPDATE User_info SET topic_id = NULL WHERE user_id = ?;", (user_id,))


@sql_kit(DB_PATH)
def get_week(user_id: int, _cursor: sqlite3.Cursor) -> int:
    """
    Возвращает значение поля week - недели. 1 - "Числитель", 2 - "Знаменатель"
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`int` Неделя. 1 - "Числитель", 2 - "Знаменатель"
    """
    _cursor.execute("""
        SELECT week FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return int(result[0]) if result else None


@sql_kit(DB_PATH)
def set_week(user_id: int, week: int, _cursor: sqlite3.Cursor) -> None:
    """
    Устанавливает значение поля week. 1 - "Числитель", 2 - "Знаменатель"
    :param user_id:  :class:`int` user id
    :param week:  :class:`int` Неделя. 1 - "Числитель", 2 - "Знаменатель"
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, week)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET week=excluded.week;
        """, (user_id, week))


@sql_kit(DB_PATH)
def get_day(user_id: int, _cursor: sqlite3.Cursor) -> int:
    """
    Возвращает значение поля day. 1 - "Понедельник", 2 - "Вторник" ... 6 - "Суббота"
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`int` День. 1 - "Понедельник", 2 - "Вторник" ... 6 - "Суббота"
    """
    _cursor.execute("""
        SELECT day FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_day(user_id: int, day: int, _cursor: sqlite3.Cursor) -> None:
    """
    Возвращает значение поля day. 1 - "Понедельник", 2 - "Вторник" ... 6 - "Суббота"
    :param user_id:  :class:`int` user id
    :param day:  :class:`int` День. 1 - "Понедельник", 2 - "Вторник" ... 6 - "Суббота"
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, day)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET day=excluded.day;
        """, (user_id, day))


@sql_kit(DB_PATH)
def get_room(user_id: int, _cursor: sqlite3.Cursor) -> str:
    """
    Возвращает значение поля room - аудитория
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` Аудитория
    """
    _cursor.execute("""SELECT room FROM Temp_Data
        WHERE user_id = ?
        """, (user_id,))
    result = _cursor.fetchone()
    return result[0] if result else None


@sql_kit(DB_PATH)
def set_room(user_id: int, room: str, _cursor: sqlite3.Cursor):
    """
    Устанавливает значение для поля room - аудитория
    :param user_id:  :class:`int` user id
    :param room:  :class:`str` Аудитория
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    """
    _cursor.execute("""
        INSERT INTO Temp_Data(user_id, room)
        VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
        SET room=excluded.room;
        """, (user_id, room))


@sql_kit(DB_PATH)
def get_user_info(user_id, _cursor: sqlite3.Cursor):
    """
    Возвращает информацию о пользователе, подготовленную к отправке админу
    :param user_id:  :class:`int` user id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` Информация о пользователе
    """
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
`blocked``     ``{data[8]}`
`banned``      ``{data[9]}`
"""


@sql_kit(DB_PATH)
def get_all_user_ids(_cursor: sqlite3.Cursor) -> list:
    """
    Возвращает список всех user_id
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`list` Список всех user_id
    """
    _cursor.execute("SELECT user_id FROM User_Info")
    return [row[0] for row in _cursor.fetchall()]


@sql_kit(DB_PATH)
def get_all_users_info(_cursor: sqlite3.Cursor) -> str:
    """
    Возвращает информацию о всех пользователях, подготовленную к отправке админу
    :param _cursor:  :class:`sqlite3.Cursor` Не нужно передавать
    :return:  :class:`str` Информация о всех пользователях
    """
    # Подсчёт количества пользователей, когда-либо заходивших в бота
    _cursor.execute("SELECT COUNT(*) FROM User_Info")
    users_count = _cursor.fetchone()[0]

    # Подсчет количества пользователей с last_date не старше одной недели
    _cursor.execute("SELECT last_date FROM User_Info")
    users = _cursor.fetchall()
    recent_users_count = 0
    today = datetime.today().date()
    for (last_date_str,) in users:
        last_date = datetime.strptime(last_date_str, '%d-%m-%Y %H:%M:%S').date()
        days_until = (last_date - today).days
        if days_until >= 0:
            recent_users_count += 1

    _cursor.execute("SELECT COUNT(*) FROM User_Info WHERE blocked = 1")
    blocked_count = _cursor.fetchone()[0]

    _cursor.execute("SELECT COUNT(*) FROM User_Info WHERE banned = 1")
    banned_count = _cursor.fetchone()[0]

    result = (f"Пользователей: {users_count}\n"
              f"Активных: {recent_users_count}\n"
              f"Заблокировали бота: {blocked_count}\n"
              f"Забанено: {banned_count}")
    return result


async def broadcast_message(bot, text: str) -> None:
    """
    Отправляет сообщение всем пользователям, которые не заблокировали бота
    :param bot:  :class:`aiogram.Bot` Бот
    :param text:  :class:`str` Текст сообщения
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
    day = int(f"{datetime.now().weekday() + 1}")
    week = 2 if datetime.now().isocalendar()[1] % 2 == 0 else 1
    if day == 7:
        set_day(user_id, 1)
        set_week(user_id, week + 1 if week == 1 else week - 1)
    else:
        set_day(user_id, day)
        set_week(user_id, week)
