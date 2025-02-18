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

from app.config import COLLEGE_CONST, SCHEDULE_DB


class Schedule:
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", ]

    def __init__(self):
        self.__conn = sqlite3.connect(SCHEDULE_DB)
        self.__cursor = self.__conn.cursor()

    def add_schedule(self, time: str, day_name: str, week_type: str, group_id: int, teacher_id: int, room_id: int,
            subject_id: int, college: bool = False, ) -> None:
        params = [time, day_name, week_type, group_id, teacher_id, room_id, subject_id, ]
        self.__cursor.execute("""
            SELECT s.ScheduleID
            FROM (
                SELECT ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID FROM Schedule
                UNION ALL
                SELECT ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID FROM CollegeSchedule
            ) s
            WHERE (Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) = (?, ?, ?, ?, ?, ?, ?)
            """, tuple(params), )
        if self.__cursor.fetchone():
            return
        if college:
            self.__cursor.execute("SELECT MAX(ScheduleID) FROM CollegeSchedule")
            max_id = self.__cursor.fetchone()[0]
            params.insert(0, max_id + 1 if max_id is not None else COLLEGE_CONST + 1)
            self.__cursor.execute(
                "INSERT INTO CollegeSchedule (ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                tuple(params), )
        else:
            self.__cursor.execute("SELECT MAX(ScheduleID) FROM Schedule")
            max_id = self.__cursor.fetchone()[0]
            params.insert(0, max_id + 1 if max_id is not None else 1)
            self.__cursor.execute(
                "INSERT INTO Schedule (ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                tuple(params), )
        self.__conn.commit()

    def add_subject(self, subject_name: str) -> int:
        self.__cursor.execute("SELECT SubjectID FROM Subjects WHERE SubjectName = ?", (subject_name,))
        subject_id = self.__cursor.fetchone()
        if subject_id:
            return subject_id[0]
        self.__cursor.execute("SELECT MAX(SubjectID) FROM Subjects")
        max_id = self.__cursor.fetchone()[0]
        subject_id = max_id + 1 if max_id is not None else 1
        self.__cursor.execute("INSERT INTO Subjects (SubjectName, SubjectID) VALUES (?, ?)",
            (subject_name, subject_id), )
        self.__conn.commit()
        return subject_id

    def add_group(self, group_name: str) -> int:
        self.__cursor.execute("SELECT GroupID FROM Groups WHERE GroupName = ?", (group_name,))
        group_id = self.__cursor.fetchone()
        if group_id:
            return group_id[0]
        self.__cursor.execute("SELECT MAX(GroupID) FROM Groups")
        self.__cursor.execute("INSERT INTO Groups (GroupName) VALUES (?)", (group_name,))
        group_id = self.__cursor.lastrowid
        self.__conn.commit()
        return group_id

    def add_teacher(self, teacher_name: str) -> int:
        self.__cursor.execute("SELECT TeacherID FROM Teachers WHERE TeacherName = ?", (teacher_name,))
        teacher_id = self.__cursor.fetchone()
        if teacher_id:
            return teacher_id[0]
        self.__cursor.execute("SELECT MAX(TeacherID) FROM Teachers")
        self.__cursor.execute("INSERT INTO Teachers (TeacherName) VALUES (?)", (teacher_name,))
        teacher_id = self.__cursor.lastrowid
        self.__conn.commit()
        return teacher_id

    def add_room(self, room_name: str) -> int:
        self.__cursor.execute("SELECT RoomID FROM Rooms WHERE RoomName = ?", (room_name,))
        room_id = self.__cursor.fetchone()
        if room_id:
            return room_id[0]
        self.__cursor.execute("SELECT MAX(RoomID) FROM Rooms")
        self.__cursor.execute("INSERT INTO Rooms (RoomName) VALUES (?)", (room_name,))
        room_id = self.__cursor.lastrowid
        self.__conn.commit()
        return room_id

    def get_group_name(self, group_id: int) -> str:
        self.__cursor.execute("SELECT GroupName FROM Groups WHERE GroupID = ?", (group_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def get_group_id(self, group_name: str) -> int:
        self.__cursor.execute("SELECT GroupID FROM Groups WHERE GroupName = ?", (group_name,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def get_teacher_name(self, teacher_id: int) -> str:
        self.__cursor.execute("SELECT TeacherName FROM Teachers WHERE TeacherID = ?", (teacher_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def get_teacher_id(self, teacher_name: str) -> int:
        self.__cursor.execute("SELECT TeacherID FROM Teachers WHERE TeacherName = ?", (teacher_name,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def get_room_name(self, room_id: int) -> str:
        self.__cursor.execute("SELECT RoomName FROM Rooms WHERE RoomID = ?", (room_id,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def get_room_id(self, room_name: str) -> int:
        self.__cursor.execute("SELECT RoomID FROM Rooms WHERE RoomName = ?", (room_name,))
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def clear_university(self) -> None:
        self.__cursor.execute(f"DELETE FROM Schedule")
        self.__cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='Schedule'")

    def clear_college(self) -> None:
        self.__cursor.execute(f"DELETE FROM CollegeSchedule")
        self.__cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='CollegeSchedule'")

    def __del__(self):
        self.__conn.close()
