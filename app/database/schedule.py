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

from app.config import COLLEGE_CONST, SCHEDULE_DB, STUDENTS


class Schedule:
    days_of_week = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
    ]

    def __init__(self):
        self.__conn = sqlite3.connect(SCHEDULE_DB)
        self.__cursor = self.__conn.cursor()

    def get_schedule_id_by_teacher(self, day: int, week: int, teacher_name: str) -> list[int]:
        query = """
            SELECT s.ScheduleID
            FROM (
                SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, TeacherID FROM Schedule
                UNION ALL
                SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, TeacherID FROM CollegeSchedule
            ) s
            JOIN Subjects sub ON s.SubjectID = sub.SubjectID
            JOIN Teachers t ON s.TeacherID = t.TeacherID
            WHERE t.TeacherName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
            ORDER BY s.Time
            """
        self.__cursor.execute(
            query,
            (
                teacher_name,
                self.days_of_week[day - 1],
                "Числитель" if week == 1 else "Знаменатель",
            ),
        )
        result = self.__cursor.fetchall()
        if teacher_name in STUDENTS:
            group_result = self.get_schedule_id_by_group(day, week, STUDENTS[teacher_name])
            result.extend([(i,) for i in group_result])
        if result is None:
            return []
        return [row[0] for row in result]

    def get_schedule_id_by_group(self, day: int, week: int, group_name: str) -> list[int]:
        query = """
            SELECT s.ScheduleID
            FROM (
                SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, GroupID FROM Schedule
                UNION ALL
                SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, GroupID FROM CollegeSchedule
            ) s
            JOIN Subjects sub ON s.SubjectID = sub.SubjectID
            JOIN Groups g ON s.GroupID = g.GroupID
            WHERE g.GroupName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
            ORDER BY s.Time
            """
        self.__cursor.execute(
            query,
            (
                group_name,
                self.days_of_week[day - 1],
                "Числитель" if week == 1 else "Знаменатель",
            ),
        )
        result = self.__cursor.fetchall()
        if result is None:
            return []
        return [row[0] for row in result]

    def get_schedule_id_by_room(self, day: int, week: int, room_name: str) -> list[int]:
        query = """
            SELECT s.ScheduleID
            FROM (
                SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, RoomID FROM Schedule
                UNION ALL
                SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, RoomID FROM CollegeSchedule
            ) s
            JOIN Subjects sub ON s.SubjectID = sub.SubjectID
            JOIN Rooms r ON s.RoomID = r.RoomID
            WHERE r.RoomName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
            ORDER BY s.Time
            """
        self.__cursor.execute(
            query,
            (
                room_name,
                self.days_of_week[day - 1],
                "Числитель" if week == 1 else "Знаменатель",
            ),
        )
        result = self.__cursor.fetchall()
        if result is None:
            return []
        return [row[0] for row in result]

    def edit_time(self, schedule_id: int, time: str) -> None:
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                "UPDATE Schedule SET Time = ? WHERE ScheduleID = ?",
                (
                    time,
                    schedule_id,
                ),
            )
        else:
            self.__cursor.execute(
                "UPDATE CollegeSchedule SET Time = ? WHERE ScheduleID = ?",
                (time, schedule_id),
            )
        self.__conn.commit()

    def edit_day(self, schedule_id: int, day: str) -> None:
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                "UPDATE Schedule SET DayOfWeek = ? WHERE ScheduleID = ?",
                (
                    day,
                    schedule_id,
                ),
            )
        else:
            self.__cursor.execute(
                "UPDATE CollegeSchedule SET DayOfWeek = ? WHERE ScheduleID = ?",
                (day, schedule_id),
            )
        self.__conn.commit()

    def edit_week(self, schedule_id: int, week: str) -> None:
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                "UPDATE Schedule SET WeekType = ? WHERE ScheduleID = ?",
                (
                    week,
                    schedule_id,
                ),
            )
        else:
            self.__cursor.execute(
                "UPDATE CollegeSchedule SET WeekType = ? WHERE ScheduleID = ?",
                (week, schedule_id),
            )
        self.__conn.commit()

    def edit_subject(self, schedule_id: int, subject) -> None:
        self.__cursor.execute("SELECT SubjectID FROM Subjects WHERE SubjectName = ?", (subject,))
        subject_id = self.__cursor.fetchone()[0]
        if subject_id is None:
            self.__cursor.execute(
                "INSERT INTO Subjects (SubjectName, SubjectID) VALUES (?, ?)",
                (
                    subject,
                    subject_id,
                ),
            )
            subject_id = self.__cursor.lastrowid
            self.__conn.commit()
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                "UPDATE Schedule SET SubjectID = ? WHERE ScheduleID = ?",
                (
                    subject_id,
                    schedule_id,
                ),
            )
        else:
            self.__cursor.execute(
                "UPDATE CollegeSchedule SET SubjectID = ? WHERE ScheduleID = ?",
                (subject_id, schedule_id),
            )
        self.__conn.commit()

    def edit_teacher(self, schedule_id: int, teacher) -> None:
        self.__cursor.execute("SELECT TeacherID FROM Teachers WHERE TeacherName = ?", (teacher,))
        teacher_id = self.__cursor.fetchone()[0]
        if teacher_id is None:
            self.__cursor.execute(
                "INSERT INTO Teachers (TeacherName, TeacherID) VALUES (?, ?)",
                (
                    teacher,
                    teacher_id,
                ),
            )
            teacher_id = self.__cursor.lastrowid
            self.__conn.commit()
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                "UPDATE Schedule SET TeacherID = ? WHERE ScheduleID = ?",
                (
                    teacher_id,
                    schedule_id,
                ),
            )
        else:
            self.__cursor.execute(
                "UPDATE CollegeSchedule SET TeacherID = ? WHERE ScheduleID = ?",
                (teacher_id, schedule_id),
            )
        self.__conn.commit()

    def edit_group(self, schedule_id: int, group) -> None:
        self.__cursor.execute("SELECT GroupID FROM Groups WHERE GroupName = ?", (group,))
        group_id = self.__cursor.fetchone()[0]
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                "UPDATE Schedule SET GroupID = ? WHERE ScheduleID = ?",
                (
                    group_id,
                    schedule_id,
                ),
            )
        else:
            self.__cursor.execute(
                "UPDATE CollegeSchedule SET GroupID = ? WHERE ScheduleID = ?",
                (group_id, schedule_id),
            )
        self.__conn.commit()

    def edit_room(self, schedule_id: int, room: str) -> None:
        self.__cursor.execute("SELECT RoomID FROM Rooms WHERE RoomName = ?", (room,))
        room_id = self.__cursor.fetchone()[0]
        if room_id is None:
            self.__cursor.execute("INSERT INTO Rooms (RoomName) VALUES (?)", (room,))
            room_id = self.__cursor.lastrowid
            self.__conn.commit()
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                "UPDATE Schedule SET RoomID = ? WHERE ScheduleID = ?",
                (
                    room_id,
                    schedule_id,
                ),
            )
        else:
            self.__cursor.execute(
                "UPDATE CollegeSchedule SET RoomID = ? WHERE ScheduleID = ?",
                (room_id, schedule_id),
            )
        self.__conn.commit()

    def edit_lesson_type(self, schedule_id: int, lesson_type: str) -> None:
        import re

        if schedule_id < COLLEGE_CONST:
            query = """
                SELECT sub.SubjectName
                FROM Schedule s
                JOIN Subjects sub ON s.SubjectID = sub.SubjectID
                WHERE s.ScheduleID = ?
                """
        else:
            query = """
                SELECT sub.SubjectName
                FROM CollegeSchedule s
                JOIN Subjects sub ON s.SubjectID = sub.SubjectID
                WHERE s.ScheduleID = ?
                """
        self.__cursor.execute(query, (schedule_id,))
        subject_name = self.__cursor.fetchone()[0]
        if re.search(r"\([^)]*\)", subject_name):
            subject = re.sub(r"\([^)]*\)", f"({lesson_type})", subject_name)
        else:
            subject = f"{subject_name} ({lesson_type})"
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                "UPDATE Schedule SET SubjectID = ? WHERE ScheduleID = ?",
                (
                    self.add_subject(subject),
                    schedule_id,
                ),
            )
        else:
            self.__cursor.execute(
                "UPDATE CollegeSchedule SET SubjectID = ? WHERE ScheduleID = ?",
                (self.add_subject(subject), schedule_id),
            )
        self.__conn.commit()

    def add_schedule(
        self,
        time: str,
        day_name: str,
        week_type: str,
        group_id: int,
        teacher_id: int,
        room_id: int,
        subject_id: int,
        college: bool = False,
    ) -> None:
        params = [
            time,
            day_name,
            week_type,
            group_id,
            teacher_id,
            room_id,
            subject_id,
        ]
        self.__cursor.execute(
            """
            SELECT s.ScheduleID
            FROM (
                SELECT ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID FROM Schedule
                UNION ALL
                SELECT ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID FROM CollegeSchedule
            ) s
            WHERE (Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) = (?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(params),
        )
        if self.__cursor.fetchone():
            return
        if college:
            self.__cursor.execute("SELECT MAX(ScheduleID) FROM CollegeSchedule")
            max_id = self.__cursor.fetchone()[0]
            params.insert(0, max_id + 1 if max_id is not None else COLLEGE_CONST + 1)
            self.__cursor.execute(
                "INSERT INTO CollegeSchedule (ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                tuple(params),
            )
        else:
            self.__cursor.execute("SELECT MAX(ScheduleID) FROM Schedule")
            max_id = self.__cursor.fetchone()[0]
            params.insert(0, max_id + 1 if max_id is not None else 1)
            self.__cursor.execute(
                "INSERT INTO Schedule (ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                tuple(params),
            )
        self.__conn.commit()

    def add_subject(self, subject_name: str) -> int:
        self.__cursor.execute(
            "SELECT SubjectID FROM Subjects WHERE SubjectName = ?", (subject_name,)
        )
        subject_id = self.__cursor.fetchone()
        if subject_id:
            return subject_id[0]
        self.__cursor.execute("SELECT MAX(SubjectID) FROM Subjects")
        max_id = self.__cursor.fetchone()[0]
        subject_id = max_id + 1 if max_id is not None else 1
        self.__cursor.execute(
            "INSERT INTO Subjects (SubjectName, SubjectID) VALUES (?, ?)",
            (subject_name, subject_id),
        )
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
        self.__cursor.execute(
            "SELECT TeacherID FROM Teachers WHERE TeacherName = ?", (teacher_name,)
        )
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

    def delete_schedule(self, schedule_id: int):
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute("DELETE FROM Schedule WHERE ScheduleID = ?", (schedule_id,))
        else:
            self.__cursor.execute(
                "DELETE FROM CollegeSchedule WHERE ScheduleID = ?", (schedule_id,)
            )
        self.__conn.commit()

    def get_schedule(self, schedule_id: int) -> list:
        if schedule_id < COLLEGE_CONST:
            self.__cursor.execute(
                """
                SELECT s.Time, s.DayOfWeek, s.WeekType, sub.SubjectName, GROUP_CONCAT(g.GroupName, ', ') AS GroupNames, r.RoomName, t.TeacherName
                FROM (SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, GroupID, RoomID, TeacherID FROM Schedule) s
                JOIN Subjects sub ON s.SubjectID = sub.SubjectID
                JOIN Groups g ON s.GroupID = g.GroupID
                JOIN Rooms r ON s.RoomID = r.RoomID
                JOIN Teachers t ON s.TeacherID = t.TeacherID
                WHERE s.ScheduleID = ?
                GROUP BY s.Time, sub.SubjectName, r.RoomName
                ORDER BY s.Time
                """,
                (schedule_id,),
            )
        else:
            self.__cursor.execute(
                """
                SELECT s.Time, s.DayOfWeek, s.WeekType, sub.SubjectName, g.GroupName, r.RoomName, t.TeacherName
                FROM (SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM CollegeSchedule) s
                JOIN Subjects sub ON s.SubjectID = sub.SubjectID
                JOIN Groups g ON s.GroupID = g.GroupID
                JOIN Rooms r ON s.RoomID = r.RoomID
                JOIN Teachers t ON s.TeacherID = t.TeacherID
                WHERE s.ScheduleID = ?
                ORDER BY s.Time
                """,
                (schedule_id,),
            )
        return self.__cursor.fetchall()[0]

    def get_group_name(self, group_id: int) -> str:
        self.__cursor.execute("SELECT GroupName FROM Groups WHERE GroupID = ?", (group_id,))
        return self.__cursor.fetchone()[0]

    def get_group_id(self, group_name: str) -> int:
        self.__cursor.execute("SELECT GroupID FROM Groups WHERE GroupName = ?", (group_name,))
        return self.__cursor.fetchone()[0]

    def get_teacher_name(self, teacher_id: int) -> str:
        self.__cursor.execute(
            "SELECT TeacherName FROM Teachers WHERE TeacherID = ?", (teacher_id,)
        )
        return self.__cursor.fetchone()[0]

    def get_teacher_id(self, teacher_name: str) -> int:
        self.__cursor.execute(
            "SELECT TeacherID FROM Teachers WHERE TeacherName = ?", (teacher_name,)
        )
        return self.__cursor.fetchone()[0]

    def get_room_name(self, room_id: int) -> str:
        self.__cursor.execute("SELECT RoomName FROM Rooms WHERE RoomID = ?", (room_id,))
        return self.__cursor.fetchone()[0]

    def get_room_id(self, room_name: str) -> int:
        self.__cursor.execute("SELECT RoomID FROM Rooms WHERE RoomName = ?", (room_name,))
        return self.__cursor.fetchone()[0]

    def clear_university(self) -> None:
        self.__cursor.execute(f"DELETE FROM Schedule")
        self.__cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='Schedule'")

    def clear_college(self) -> None:
        self.__cursor.execute(f"DELETE FROM CollegeSchedule")
        self.__cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='CollegeSchedule'")

    def __del__(self):
        self.__conn.close()
