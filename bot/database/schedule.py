import sqlite3

from config import COLLEGE_CONST, SCHEDULE_DB, special_teachers


class Schedule:
    def __init__(self):
        self.__conn = sqlite3.connect(SCHEDULE_DB)
        self.__cursor = self.__conn.cursor()

    def get_schedules_id(self, day: int, week: int, teacher_name: str):
        days_of_week = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
        ]
        query = """
            SELECT s.ScheduleID
            FROM (
                SELECT ScheduleID, Time, SubjectID, TeacherID, DayOfWeek, WeekType FROM Schedule
                UNION ALL
                SELECT ScheduleID, Time, SubjectID, TeacherID, DayOfWeek, WeekType FROM CollegeSchedule
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
                days_of_week[day - 1],
                "Числитель" if week == 1 else "Знаменатель",
            ),
        )
        result = self.__cursor.fetchall()
        if result is None:
            return []
        return [row[0] for row in result]

    def add_schedule(
        self,
        time: str,
        day_name: str,
        week_type: str,
        group_id: int,
        teacher_id: int,
        room_id: int,
        subject_id: int,
    ) -> None:
        self.__cursor.execute("SELECT MAX(ScheduleID) FROM Schedule")
        max_id = self.__cursor.fetchone()[0]
        schedule_id = max_id + 1 if max_id is not None else 1

        self.__cursor.execute(
            "INSERT INTO Schedule (ScheduleID, Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                schedule_id,
                time,
                day_name,
                week_type,
                group_id,
                teacher_id,
                room_id,
                subject_id,
            ),
        )
        self.__conn.commit()

    def edit_time(self, schedule_id: int, time: str) -> None:
        self.__cursor.execute(
            "UPDATE Schedule SET Time = ? WHERE ScheduleID = ?",
            (
                time,
                schedule_id,
            ),
        )
        self.__conn.commit()

    def edit_day(self, schedule_id: int, day: str) -> None:
        self.__cursor.execute(
            "UPDATE Schedule SET DayOfWeek = ? WHERE ScheduleID = ?",
            (
                day,
                schedule_id,
            ),
        )
        self.__conn.commit()

    def edit_week(self, schedule_id: int, week: str) -> None:
        self.__cursor.execute(
            "UPDATE Schedule SET WeekType = ? WHERE ScheduleID = ?",
            (
                week,
                schedule_id,
            ),
        )
        self.__conn.commit()

    def edit_subject(self, schedule_id: int, subject):
        self.__cursor.execute(
            "SELECT SubjectID FROM Subjects WHERE SubjectName = ?", (subject,)
        )
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
        self.__cursor.execute(
            "UPDATE Schedule SET SubjectID = ? WHERE ScheduleID = ?",
            (
                subject_id,
                schedule_id,
            ),
        )
        self.__conn.commit()

    def edit_teacher(self, schedule_id: int, teacher):
        self.__cursor.execute(
            "SELECT TeacherID FROM Teachers WHERE TeacherName = ?", (teacher,)
        )
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
        self.__cursor.execute(
            "UPDATE Schedule SET TeacherID = ? WHERE ScheduleID = ?",
            (
                teacher_id,
                schedule_id,
            ),
        )
        self.__conn.commit()

    def edit_group(self, schedule_id: int, group):
        self.__cursor.execute(
            "SELECT GroupID FROM Groups WHERE GroupName = ?", (group,)
        )
        group_id = self.__cursor.fetchone()[0]
        self.__cursor.execute(
            "UPDATE Schedule SET GroupID = ? WHERE ScheduleID = ?",
            (
                group_id,
                schedule_id,
            ),
        )
        self.__conn.commit()

    def edit_room(self, schedule_id: int, room: str) -> None:
        self.__cursor.execute("SELECT RoomID FROM Rooms WHERE RoomNumber = ?", (room,))
        room_id = self.__cursor.fetchone()[0]
        if room_id is None:
            self.__cursor.execute("INSERT INTO Rooms (RoomNumber) VALUES (?)", (room,))
            room_id = self.__cursor.lastrowid
            self.__conn.commit()
        self.__cursor.execute(
            "UPDATE Schedule SET RoomID = ? WHERE ScheduleID = ?",
            (
                room_id,
                schedule_id,
            ),
        )
        self.__conn.commit()

    def edit_lesson_type(self, schedule_id: int, lesson_type: str) -> None:
        import re

        query = """SELECT sub.SubjectName
            FROM (
                SELECT ScheduleID, SubjectID FROM Schedule
                UNION ALL
                SELECT ScheduleID, SubjectID FROM CollegeSchedule
            ) s
            JOIN Subjects sub ON s.SubjectID = sub.SubjectID
            WHERE s.ScheduleID = ?
            """
        self.__cursor.execute(query, (schedule_id,))
        subject_name = self.__cursor.fetchone()[0]
        # TODO: сделать проверку, есть ли уже в названии предмета тип занятия
        subject = re.sub(r"\([^)]*\)", f"({lesson_type})", subject_name)
        self.__cursor.execute(
            "UPDATE Schedule SET SubjectID = ? WHERE ScheduleID = ?",
            (
                self.add_subject(subject),
                schedule_id,
            ),
        )
        self.__conn.commit()

    def add_group(self, group_name: str) -> int:
        self.__cursor.execute(
            "SELECT GroupID FROM Groups WHERE GroupName = ?", (group_name,)
        )
        group_id = self.__cursor.fetchone()
        if group_id is None:
            self.__cursor.execute("SELECT MAX(GroupID) FROM Groups")
            self.__cursor.execute(
                "INSERT INTO Groups (GroupName) VALUES (?)", (group_name,)
            )
            group_id = self.__cursor.lastrowid
            self.__conn.commit()
        return group_id

    def add_subject(self, subject_name: str) -> int:
        self.__cursor.execute(
            "SELECT SubjectID FROM Subjects WHERE SubjectName = ?", (subject_name,)
        )
        subject_id = self.__cursor.fetchone()
        if subject_id is None:
            self.__cursor.execute("SELECT MAX(SubjectID) FROM Subjects")
            max_id = self.__cursor.fetchone()[0]
            subject_id = max_id + 1 if max_id is not None else 1
            self.__cursor.execute(
                "INSERT INTO Subjects (SubjectName, SubjectID) VALUES (?, ?)",
                (subject_name, subject_id),
            )
            self.__conn.commit()
        return subject_id

    def delete_schedule(self, schedule_id: int):
        self.__cursor.execute(
            "DELETE FROM Schedule WHERE ScheduleID = ?", (schedule_id,)
        )
        self.__conn.commit()

    def get_schedule(self, schedule_id: int) -> list:
        query = """
            SELECT s.Time, s.DayOfWeek, s.WeekType, sub.SubjectName, GROUP_CONCAT(g.GroupName, ', ') AS GroupNames, r.RoomNumber, t.TeacherName
            FROM (
                SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM Schedule
            ) s
            JOIN Subjects sub ON s.SubjectID = sub.SubjectID
            JOIN Groups g ON s.GroupID = g.GroupID
            JOIN Rooms r ON s.RoomID = r.RoomID
            JOIN Teachers t ON s.TeacherID = t.TeacherID
            WHERE s.ScheduleID = ?
            GROUP BY s.Time, sub.SubjectName, r.RoomNumber
            ORDER BY s.Time
            """
        self.__cursor.execute(query, (schedule_id,))
        return self.__cursor.fetchall()[0]

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

    def get_room_name(self, room_id: int):
        self.__cursor.execute(
            "SELECT RoomNumber FROM Rooms WHERE RoomID = ?", (room_id,)
        )
        return self.__cursor.fetchone()[0]

    def get_room_id(self, room_name: str):
        self.__cursor.execute(
            "SELECT RoomID FROM Rooms WHERE RoomNumber = ?", (room_name,)
        )
        return self.__cursor.fetchone()[0]

    def get_group_name(self, group_id: int):
        self.__cursor.execute(
            "SELECT GroupName FROM Groups WHERE GroupID = ?", (group_id,)
        )
        return self.__cursor.fetchone()[0]

    def get_group_id(self, group_name: str):
        self.__cursor.execute(
            "SELECT GroupID FROM Groups WHERE GroupName = ?", (group_name,)
        )
        return self.__cursor.fetchone()[0]

    def __del__(self):
        self.__conn.close()
