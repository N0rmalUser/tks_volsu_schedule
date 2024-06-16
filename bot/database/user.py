from aiogram.types import Message

from config import USERS_DB, timezone

from datetime import datetime

import pytz

import sqlite3


class UserDatabase:
    def __init__(self, user_id: int = None, topic_id: int = None):
        self.__conn = sqlite3.connect(USERS_DB)
        self.__cursor = self.__conn.cursor()
        if user_id is None:
            if topic_id is not None:
                self.__user_id = self.__user_id_from_topic(topic_id)
            else:
                raise ValueError('Не передан user_id или topic_id')
        else:
            self.__user_id = user_id

    @property
    def username(self) -> bool:
        self.__cursor.execute("""
            SELECT username FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        return bool(self.__cursor.fetchone()[0])

    @username.setter
    def username(self, username: str) -> None:
        self.__cursor.execute("""
            INSERT INTO User_Info(user_id, username)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET username=excluded.username;
            """, (self.__user_id, username))
        self.__conn.commit()

    @property
    def fullname(self) -> bool:
        self.__cursor.execute("""
            SELECT fullname FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        return bool(self.__cursor.fetchone()[0])

    @fullname.setter
    def fullname(self, fullname: str) -> None:
        self.__cursor.execute("""
            INSERT INTO User_Info(user_id, fullname)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET fullname=excluded.fullname;
            """, (self.__user_id, fullname))
        self.__conn.commit()

    @property
    def blocked(self) -> bool:
        self.__cursor.execute("""
            SELECT blocked FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        return bool(self.__cursor.fetchone()[0])

    @blocked.setter
    def blocked(self, block: bool) -> None:
        self.__cursor.execute("""
            INSERT INTO User_Info(user_id, blocked)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET blocked=excluded.blocked;
            """, (self.__user_id, block))
        self.__conn.commit()

    @property
    def banned(self) -> bool:
        try:
            self.__cursor.execute("""
                SELECT banned FROM User_Info
                WHERE user_id = ?
                """, (self.__user_id,))
        except Exception:
            pass
        result = self.__cursor.fetchone()
        return bool(result[0]) if result is not None else False

    @banned.setter
    def banned(self, ban: bool) -> None:
        self.__cursor.execute("""
            INSERT INTO User_Info(user_id, banned)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET banned=excluded.banned;
            """, (self.__user_id, ban))
        self.__conn.commit()

    @property
    def tracking(self) -> bool:
        self.__cursor.execute("""
            SELECT tracking FROM Temp_Data
            WHERE user_id = ?
            """, (self.__user_id,))
        try:
            return bool(self.__cursor.fetchone()[0])
        except Exception:
            return False

    @tracking.setter
    def tracking(self, tracking: bool) -> None:
        self.__cursor.execute("""
            INSERT INTO Temp_Data(user_id, tracking)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET tracking=excluded.tracking;
            """, (self.__user_id, tracking))
        self.__conn.commit()

    @property
    def type(self) -> str:
        self.__cursor.execute("""
            SELECT user_type FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        return self.__cursor.fetchone()[0]

    @type.setter
    def type(self, user_type) -> None:
        self.__cursor.execute("""
            INSERT INTO User_Info(user_id, user_type)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET user_type=excluded.user_type;
            """, (self.__user_id, user_type))
        self.__conn.commit()

    @property
    def inviter_id(self) -> int:
        self.__cursor.execute("""
            SELECT inviter_id FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        return self.__cursor.fetchone()[0]

    @inviter_id.setter
    def inviter_id(self, inviter_id: int):
        self.__cursor.execute("""
            SELECT inviter_id FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        result = self.__cursor.fetchone()
        if result is None:
            self.__cursor.execute("""
                INSERT INTO User_Info(user_id, inviter_id) 
                VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
                SET inviter_id=excluded.inviter_id;
                """, (self.__user_id, inviter_id))
        self.__conn.commit()

    @property
    def teacher(self) -> str:
        self.__cursor.execute("""
            SELECT teacher_name FROM Temp_Data
            WHERE user_id = ?
            """, (self.__user_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @teacher.setter
    def teacher(self, teacher_name: str) -> None:
        self.__cursor.execute("""
            INSERT INTO Temp_Data(user_id, teacher_name)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET teacher_name=excluded.teacher_name;
            """, (self.__user_id, teacher_name))
        self.__conn.commit()

    @property
    def group(self) -> str:
        self.__cursor.execute("""
            SELECT group_name FROM Temp_Data
            WHERE user_id = ?
            """, (self.__user_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @group.setter
    def group(self, group_name: str) -> None:
        self.__cursor.execute("""
            INSERT INTO Temp_Data(user_id, group_name)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET group_name=excluded.group_name;
            """, (self.__user_id, group_name))
        self.__conn.commit()

    @property
    def topic_id(self) -> int:
        self.__cursor.execute("""
            SELECT topic_id FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else False

    @topic_id.setter
    def topic_id(self, topic_id: int) -> None:
        self.__cursor.execute("""
            INSERT INTO User_Info(user_id, topic_id)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET topic_id=excluded.topic_id;
            """, (self.__user_id, topic_id))
        self.__conn.commit()

    @topic_id.deleter
    def topic_id(self):
        self.__cursor.execute("""
            UPDATE User_info 
            SET topic_id = NULL 
            WHERE user_id = ?;
            """, (self.__user_id,))
        self.__conn.commit()

    @property
    def week(self) -> int:
        self.__cursor.execute("""
            SELECT week FROM Temp_Data
            WHERE user_id = ?
            """, (self.__user_id,))
        result = self.__cursor.fetchone()
        return int(result[0]) if result else None

    @week.setter
    def week(self, week: int) -> None:
        self.__cursor.execute("""
            INSERT INTO Temp_Data(user_id, week)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET week=excluded.week;
            """, (self.__user_id, week))
        self.__conn.commit()

    @property
    def day(self) -> int:
        self.__cursor.execute("""
            SELECT day FROM Temp_Data
            WHERE user_id = ?
            """, (self.__user_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @day.setter
    def day(self, day: int) -> None:
        self.__cursor.execute("""
            INSERT INTO Temp_Data(user_id, day)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET day=excluded.day;
            """, (self.__user_id, day))
        self.__conn.commit()

    @property
    def default(self):
        self.__cursor.execute("""
            SELECT defaulte FROM Temp_Data
            WHERE user_id = ?
            """, (self.__user_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @default.setter
    def default(self, default: str):
        self.__cursor.execute("""
            INSERT INTO Temp_Data(user_id, defaulte)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET defaulte=excluded.defaulte;
            """, (self.__user_id, default))
        self.__conn.commit()

    @property
    def  last_date(self):
        self.__cursor.execute("""
            SELECT last_date FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @last_date.setter
    def last_date(self, msg: Message) -> None:
        formatted_last_date = (msg.date
                               .astimezone(pytz.timezone(timezone))
                               .strftime('%d-%m-%Y %H:%M:%S'))
        self.__cursor.execute("""
            INSERT INTO User_Info(user_id, last_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET last_date=excluded.last_date;
            """, (msg.from_user.id, formatted_last_date))
        self.__conn.commit()

    @property
    def start_date(self) -> str:
        self.__cursor.execute("""
            SELECT start_date FROM User_Info
            WHERE user_id = ?
            """, (self.__user_id,))
        return self.__cursor.fetchone()[0]

    @start_date.setter
    def start_date(self, date: str) -> None:
        self.__cursor.execute("""
            INSERT INTO User_Info(user_id, start_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET start_date=excluded.start_date;
            """, (self.__user_id, date))
        self.__conn.commit()

    def tg_id(self) -> int:
        return self.__user_id

    def set_today_date(self) -> None:
        """Устанавливает день и неделю в зависимости от текущей даты"""
        day = int(f"{datetime.now(pytz.timezone(timezone)).weekday() + 1}")
        week = 2 if datetime.now(pytz.timezone(timezone)).isocalendar()[1] % 2 == 0 else 1
        if day == 7:
            self.day = 1
            self.week = week + 1 if week == 1 else week - 1
        else:
            self.day = day
            self.week = week

    def exists(self) -> bool:
        """Проверяет, есть ли пользователь в базе данных"""
        self.__cursor.execute("""
            SELECT * 
            FROM User_Info 
            WHERE user_id = ?
            """, (self.__user_id,))
        return True if self.__cursor.fetchone() is not None else False

    def __user_id_from_topic(self, topic_id: int) -> int:
        """Возвращает значение поля user_id по значению поля topic_id"""
        self.__cursor.execute("""
            SELECT user_id FROM User_Info
            WHERE topic_id = ?
            """, (topic_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def __del__(self):
        self.__conn.close()
