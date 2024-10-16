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

import pytz
from aiogram.types import Message

from app.config import NUMERATOR, TIMEZONE, USERS_DB


class UserDatabase:
    def __init__(self, user_id: int = None, topic_id: int = None):
        """Класс для работы с базой данных пользователей. Позволяет получать и устанавливать данные пользователя в базе данных."""

        self.__conn = sqlite3.connect(USERS_DB)
        self.__cursor = self.__conn.cursor()
        if user_id is None:
            if topic_id is None:
                raise ValueError("Не передан user_id или topic_id")
            self.__user_id = self.__user_id_from_topic(topic_id)
        else:
            self.__user_id = user_id

    @property
    def username(self) -> bool:
        """Возвращает username пользователя из базы данных"""

        self.__cursor.execute(
            """
            SELECT username FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @username.setter
    def username(self, username: str) -> None:
        """Устанавливает username телеграмма (@кто-то) пользователя в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, username)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET username=excluded.username;
            """,
            (self.__user_id, username),
        )
        self.__conn.commit()

    @property
    def fullname(self) -> bool:
        """Возвращает полное имя пользователя из базы данных."""

        self.__cursor.execute(
            """
            SELECT fullname FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @fullname.setter
    def fullname(self, fullname: str) -> None:
        """Устанавливает полное имя пользователя в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, fullname)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET fullname=excluded.fullname;
            """,
            (self.__user_id, fullname),
        )
        self.__conn.commit()

    @property
    def blocked(self) -> bool:
        """Возвращает значение blocked из базы данных. Если blocked = True, то пользователь заблокировал бота."""

        self.__cursor.execute(
            """
            SELECT blocked FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return bool(result[0]) if result is not None else False

    @blocked.setter
    def blocked(self, block: bool) -> None:
        """Устанавливает значение blocked в базе данных. Если blocked = True, то пользователь заблокировал бота."""

        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, blocked)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET blocked=excluded.blocked;
            """,
            (self.__user_id, block),
        )
        self.__conn.commit()

    @property
    def banned(self) -> bool:
        """Возвращает значение banned из базы данных. Если banned = True, то пользователь заблокирован."""

        self.__cursor.execute(
            """
            SELECT banned FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return bool(result[0]) if result is not None else False

    @banned.setter
    def banned(self, ban: bool) -> None:
        """Устанавливает значение banned в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, banned)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET banned=excluded.banned;
            """,
            (self.__user_id, ban),
        )
        self.__conn.commit()

    @property
    def tracking(self) -> bool:
        """Возвращает значение tracking из базы данных. Если tracking = True, то отслеживание действий пользователя включено."""

        self.__cursor.execute(
            """
            SELECT tracking FROM Temp_Data
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return bool(result[0]) if result is not None else False

    @tracking.setter
    def tracking(self, tracking: bool) -> None:
        """Устанавливает значение tracking в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO Temp_Data(user_id, tracking)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET tracking=excluded.tracking;
            """,
            (self.__user_id, tracking),
        )
        self.__conn.commit()

    @property
    def type(self) -> str:
        """Возвращает тип пользователя из базы данных. Могут быть student или teacher"""

        self.__cursor.execute(
            """
            SELECT user_type FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @type.setter
    def type(self, user_type) -> None:
        """Устанавливает тип пользователя в базе данных. Могут быть student или teacher"""

        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, user_type)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET user_type=excluded.user_type;
            """,
            (self.__user_id, user_type),
        )
        self.__conn.commit()

    @property
    def inviter_id(self) -> int:
        """Возвращает id пригласившего пользователя из базы данных"""

        self.__cursor.execute(
            """
            SELECT inviter_id FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @inviter_id.setter
    def inviter_id(self, inviter_id: int):
        """Устанавливает id пригласившего пользователя в базе данных"""

        self.__cursor.execute(
            """
            SELECT inviter_id FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        if result is None:
            self.__cursor.execute(
                """
                INSERT INTO User_Info(user_id, inviter_id) 
                VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
                SET inviter_id=excluded.inviter_id;
                """,
                (self.__user_id, inviter_id),
            )
        self.__conn.commit()

    @property
    def teacher(self) -> int:
        """Возвращает преподавателя пользователя из базы данных"""

        self.__cursor.execute(
            """
            SELECT teacher_id FROM Temp_Data
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @teacher.setter
    def teacher(self, teacher_id: int) -> None:
        """Устанавливает преподавателя пользователя в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO Temp_Data(user_id, teacher_id)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET teacher_id=excluded.teacher_id;
            """,
            (self.__user_id, teacher_id),
        )
        self.__conn.commit()

    @property
    def group(self) -> int:
        """Возвращает группу пользователя из базы данных"""

        self.__cursor.execute(
            """
            SELECT group_id FROM Temp_Data
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @group.setter
    def group(self, group_id: str) -> None:
        """Устанавливает группу пользователя в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO Temp_Data(user_id, group_id)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET group_id=excluded.group_id;
            """,
            (self.__user_id, group_id),
        )
        self.__conn.commit()

    @property
    def topic_id(self) -> int:
        """Возвращает topic_id пользователя из базы данных"""

        self.__cursor.execute(
            """
            SELECT topic_id FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else False

    @topic_id.setter
    def topic_id(self, topic_id: int) -> None:
        """Устанавливает topic_id пользователя в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, topic_id)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET topic_id=excluded.topic_id;
            """,
            (self.__user_id, topic_id),
        )
        self.__conn.commit()

    @topic_id.deleter
    def topic_id(self):
        """Удаляет topic_id пользователя из базы данных"""

        self.__cursor.execute(
            """
            UPDATE User_info 
            SET topic_id = NULL 
            WHERE user_id = ?;
            """,
            (self.__user_id,),
        )
        self.__conn.commit()

    @property
    def week(self) -> int:
        """Возвращает неделю, выбранную пользователем"""

        self.__cursor.execute(
            """
            SELECT week FROM Temp_Data
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return int(result[0]) if result else None

    @week.setter
    def week(self, week: int) -> None:
        """Устанавливает неделю, выбранную пользователем"""

        self.__cursor.execute(
            """
            INSERT INTO Temp_Data(user_id, week)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET week=excluded.week;
            """,
            (self.__user_id, week),
        )
        self.__conn.commit()

    @property
    def day(self) -> int:
        """Возвращает день недели, выбранный пользователь"""

        self.__cursor.execute(
            """
            SELECT day FROM Temp_Data
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @day.setter
    def day(self, day: int) -> None:
        """Устанавливает день недели, выбранный пользователь"""

        self.__cursor.execute(
            """
            INSERT INTO Temp_Data(user_id, day)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET day=excluded.day;
            """,
            (self.__user_id, day),
        )
        self.__conn.commit()

    @property
    def default(self):
        """Возвращает группу или преподавателя по умолчанию"""

        self.__cursor.execute(
            """
            SELECT defaulte FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @default.setter
    def default(self, default: str):
        """Устанавливает группу или преподавателя по умолчанию"""

        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, defaulte)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET defaulte=excluded.defaulte;
            """,
            (self.__user_id, default),
        )
        self.__conn.commit()

    @property
    def last_date(self):
        """Возвращает последнюю дату использования бота пользователем"""

        self.__cursor.execute(
            """
            SELECT last_date FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @last_date.setter
    def last_date(self, msg: Message) -> None:
        """Устанавливает последнюю дату использования бота пользователем"""

        formatted_last_date = msg.date.astimezone(pytz.timezone(TIMEZONE)).strftime(
            "%d-%m-%Y %H:%M:%S"
        )
        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, last_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET last_date=excluded.last_date;
            """,
            (msg.from_user.id, formatted_last_date),
        )
        self.__conn.commit()

    @property
    def start_date(self) -> str:
        """Возвращает дату регистрации пользователя"""

        self.__cursor.execute(
            """
            SELECT start_date FROM User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @start_date.setter
    def start_date(self, date: str) -> None:
        """Устанавливает дату регистрации пользователя"""

        self.__cursor.execute(
            """
            INSERT INTO User_Info(user_id, start_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET start_date=excluded.start_date;
            """,
            (self.__user_id, date),
        )
        self.__conn.commit()

    def tg_id(self) -> int:
        """Возвращает user_id пользователя"""

        return self.__user_id

    def set_today_date(self) -> None:
        """Устанавливает день и неделю в зависимости от текущей даты"""

        day = int(f"{datetime.now(pytz.timezone(TIMEZONE)).weekday() + 1}")
        week_int = 2 if NUMERATOR == 0 else 1
        week = (
            week_int
            if datetime.now(pytz.timezone(TIMEZONE)).isocalendar()[1] % 2 == 0
            else 3 - week_int
        )
        if day == 7:
            self.day = 1
            self.week = week + 1 if week == 1 else week - 1
        else:
            self.day = day
            self.week = week

    def exists(self) -> bool:
        """Проверяет, есть ли пользователь в базе данных"""

        self.__cursor.execute(
            """
            SELECT * 
            FROM User_Info 
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        return True if self.__cursor.fetchone() is not None else False

    def __user_id_from_topic(self, topic_id: int) -> int:
        """Возвращает значение поля user_id по значению поля topic_id"""

        self.__cursor.execute(
            """
            SELECT user_id FROM User_Info
            WHERE topic_id = ?
            """,
            (topic_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def __del__(self):
        self.__conn.close()
