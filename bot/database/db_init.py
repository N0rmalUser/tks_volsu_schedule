import sqlite3

from bot.database.utils import sql_kit
from config import ACTIVITIES_DB, SCHEDULE_DB, USERS_DB


@sql_kit(USERS_DB)
def user_db_init(cursor: sqlite3.Cursor):
    cursor.execute(
        """
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
            defaulte TEXT,
            FOREIGN KEY (inviter_id) REFERENCES User_Info(user_id)
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Temp_Data (
            user_id INTEGER PRIMARY KEY,
            tracking BOOLEAN DEFAULT false,
            week INTEGER,
            day INTEGER,
            teacher_name TEXT,
            group_name TEXT,
            FOREIGN KEY (user_id) REFERENCES User_Info(user_id)
        )
    """
    )


@sql_kit(SCHEDULE_DB)
def schedule_db_init(cursor: sqlite3.Cursor):
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Rooms (
                        RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
                        RoomNumber TEXT UNIQUE NOT NULL)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Groups (
                        GroupID INTEGER PRIMARY KEY AUTOINCREMENT,
                        GroupName TEXT UNIQUE NOT NULL)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Teachers (
                        TeacherID INTEGER PRIMARY KEY AUTOINCREMENT,
                        TeacherName TEXT UNIQUE NOT NULL)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Subjects (
                        SubjectID INTEGER PRIMARY KEY AUTOINCREMENT,
                        SubjectName TEXT UNIQUE NOT NULL)"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Schedule (
                        ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Time TEXT NOT NULL,
                        DayOfWeek TEXT NOT NULL,
                        WeekType TEXT NOT NULL,
                        GroupID INTEGER,
                        TeacherID INTEGER,
                        RoomID INTEGER,
                        SubjectID INTEGER,
                        FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
                        FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
                        FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
                        FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID))"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS CollegeSchedule (
                            ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
                            Time TEXT NOT NULL,
                            DayOfWeek TEXT NOT NULL,
                            WeekType TEXT NOT NULL,
                            GroupID INTEGER,
                            TeacherID INTEGER,
                            RoomID INTEGER,
                            SubjectID INTEGER,
                            FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
                            FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
                            FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
                            FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID))"""
    )


@sql_kit(ACTIVITIES_DB)
def activity_db_init(cursor: sqlite3.Cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS User_Activity_Stats (
            date TEXT,
            hour INTEGER,
            user_count INTEGER,
            PRIMARY KEY (date, hour)
        );
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS User_Unique_Activity (
            date TEXT,
            hour INTEGER,
            user_id INTEGER,
            PRIMARY KEY (date, hour, user_id)
        );
    """
    )


def db_init():
    """Инициализация базы данных"""

    import logging

    try:
        user_db_init()
        schedule_db_init()
        activity_db_init()
        logging.info("База данных инициализирована")
    except Exception as e:
        logging.error(f"Ошибка в инициализации базы данных: {e}")
        raise e
