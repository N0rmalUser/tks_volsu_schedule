import sqlite3

from app.config import VK_DB


class VkUser:
    def __init__(self, user_id: int) -> None:
        self.__conn = sqlite3.connect(VK_DB)
        self.__cursor = self.__conn.cursor()
        self.__user_id = user_id

    @property
    def id(self) -> int:
        """Возвращает user_id пользователя"""

        return self.__user_id

    @property
    def user_type(self) -> str:
        """Возвращает тип пользователя из базы данных. Могут быть student или teacher"""

        self.__cursor.execute(
            """
            SELECT user_type FROM Vk_User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        return self.__cursor.fetchone()[0]

    @user_type.setter
    def user_type(self, user_type: str) -> None:
        """Устанавливает тип пользователя в базе данных. Могут быть student или teacher"""

        self.__cursor.execute(
            """
            INSERT INTO Vk_User_Info(user_id, user_type)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET user_type=excluded.user_type;
            """,
            (self.__user_id, user_type),
        )
        self.__conn.commit()

    @property
    def teacher(self) -> int:
        """Возвращает преподавателя пользователя из базы данных"""

        self.__cursor.execute(
            """
            SELECT teacher_id FROM Vk_User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        return row[0] if (row := self.__cursor.fetchone()) else None

    @teacher.setter
    def teacher(self, teacher_id: int) -> None:
        """Устанавливает преподавателя пользователя в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO Vk_User_Info(user_id, teacher_id)
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
            SELECT group_id FROM Vk_User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        return row[0] if (row := self.__cursor.fetchone()) else None

    @group.setter
    def group(self, group_id: str) -> None:
        """Устанавливает группу пользователя в базе данных"""

        self.__cursor.execute(
            """
            INSERT INTO Vk_User_Info(user_id, group_id)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET group_id=excluded.group_id;
            """,
            (self.__user_id, group_id),
        )
        self.__conn.commit()

    @property
    def last_date(self) -> str | None:
        """Возвращает последнюю дату использования бота пользователем"""

        self.__cursor.execute(
            """
            SELECT last_date FROM Vk_User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        return row[0] if (row := self.__cursor.fetchone()) else None

    @last_date.setter
    def last_date(self, date: str) -> None:
        """Устанавливает последнюю дату использования бота пользователем"""

        self.__cursor.execute(
            """
            INSERT INTO Vk_User_Info(user_id, last_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET last_date=excluded.last_date;
            """,
            (self.__user_id, date),
        )
        self.__conn.commit()

    @property
    def start_date(self) -> str:
        """Возвращает дату регистрации пользователя"""

        self.__cursor.execute(
            """
            SELECT start_date FROM Vk_User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        return row[0] if (row := self.__cursor.fetchone()) else None

    @start_date.setter
    def start_date(self, date: str) -> None:
        self.__cursor.execute(
            """
            INSERT INTO Vk_User_Info(user_id, start_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET start_date=excluded.start_date;
            """,
            (self.__user_id, date),
        )
        self.__conn.commit()

    def is_exists(self) -> bool:
        """Проверяет, есть ли пользователь в базе данных"""

        self.__cursor.execute(
            """
            SELECT *
            FROM Vk_User_Info
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        return True if self.__cursor.fetchone() else False

    def __del__(self) -> None:
        self.__conn.close()
