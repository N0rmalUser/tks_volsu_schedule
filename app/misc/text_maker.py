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

import re
import sqlite3

from app import config
from app.database import sql_kit


@sql_kit(config.SCHEDULE_DB)
def get_group_schedule(
    day: int,
    week: int,
    group_name: str,
    editing: bool = False,
    cursor: sqlite3.Cursor = None,
):
    """Возвращает отформатированное расписание для указанной группы на указанный день и неделю"""

    from app.misc import get_lesson_label, get_time_symbol, time_to_minutes

    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    query = """
        SELECT GROUP_CONCAT(s.ScheduleID, ', '), s.Time, sub.SubjectName, r.RoomName, t.TeacherName
        FROM (
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM Schedule
            UNION ALL
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM CollegeSchedule
        ) s        
        JOIN Subjects sub ON s.SubjectID = sub.SubjectID
        JOIN Groups g ON s.GroupID = g.GroupID
        JOIN Rooms r ON s.RoomID = r.RoomID
        JOIN Teachers t ON s.TeacherID = t.TeacherID
        WHERE g.GroupName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
        GROUP BY s.Time, sub.SubjectName, r.RoomName
        ORDER BY s.Time
        """

    cursor.execute(query, (group_name, days_of_week[day - 1], week_type))
    rows = cursor.fetchall()

    schedule = []
    for row in rows:
        schedule_id, time, subject, room_name, teacher = row
        schedule.append(
            {
                "schedule_id": schedule_id,
                "time": time,
                "subject": subject,
                "room": room_name,
                "teacher": teacher,
            }
        )
    text = header = f"{days_of_week[day - 1]}       {week_type}\n{group_name}\n\n"
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x["time"]))
        for lesson in sorted_lessons:
            subject = re.sub(r"\([^)]*\)", "", lesson["subject"])

            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", lesson["subject"])))
            text += f"👨🏻‍💻 {lesson['schedule_id']}\n" if editing else ""
            text += (
                f"{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n"
                f"📖 {subject}\n"
                f"👨‍🏫 {lesson['teacher']}\n"
                f"🏠 Ауд. {lesson['room']}\n\n"
            )
        return text
    else:
        return f"{header}Сегодня пар нет!"


@sql_kit(config.SCHEDULE_DB)
def get_teacher_schedule(
    day: int,
    week: int,
    teacher_name: str,
    editing: bool = False,
    cursor: sqlite3.Cursor = None,
):
    """Возвращает отформатированное расписание для указанного преподавателя на указанный день и неделю. Если преподаватель обучается в какой-либо группе (указывается в config.py), то возвращает расписание для этой группы, смешанное с расписанием преподавателя."""

    from app.misc import get_lesson_label, get_time_symbol, time_to_minutes

    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    schedule = []
    if teacher_name in config.STUDENTS.keys():

        query = """
            SELECT s.ScheduleID, s.Time, sub.SubjectName, r.RoomName, t.TeacherName
            FROM (
                SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM Schedule
                UNION ALL
                SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM CollegeSchedule
            ) s
            JOIN Subjects sub ON s.SubjectID = sub.SubjectID
            JOIN Groups g ON s.GroupID = g.GroupID
            JOIN Rooms r ON s.RoomID = r.RoomID
            JOIN Teachers t ON s.TeacherID = t.TeacherID
            WHERE g.GroupName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
            ORDER BY s.Time;
            """

        cursor.execute(
            query,
            (config.STUDENTS[teacher_name], days_of_week[day - 1], week_type),
        )
        rows = cursor.fetchall()
        for row in rows:
            schedule_id, time, subject, room_name, teacher = row
            schedule.append(
                {
                    "schedule_id": schedule_id,
                    "time": time,
                    "subject": subject,
                    "room": room_name,
                    "teacher": teacher,
                }
            )

    query = """
        SELECT GROUP_CONCAT(s.ScheduleID, ', '), s.Time, sub.SubjectName, GROUP_CONCAT(g.GroupName, ', ') AS GroupNames, r.RoomName
        FROM (
            SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, GroupID, RoomID, TeacherID FROM Schedule
            UNION ALL
            SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, GroupID, RoomID, TeacherID FROM CollegeSchedule
        ) s
        JOIN Subjects sub ON s.SubjectID = sub.SubjectID
        JOIN Groups g ON s.GroupID = g.GroupID
        JOIN Rooms r ON s.RoomID = r.RoomID
        JOIN Teachers t ON s.TeacherID = t.TeacherID
        WHERE t.TeacherName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
        GROUP BY s.Time, sub.SubjectName, r.RoomName
        ORDER BY s.Time
        """

    cursor.execute(query, (teacher_name, days_of_week[day - 1], week_type))
    rows = cursor.fetchall()
    for row in rows:
        schedule_id, time, subject, group, room_name = row
        schedule.append(
            {
                "schedule_id": schedule_id,
                "time": time,
                "subject": subject,
                "group": group,
                "room": room_name,
            }
        )
    text = header = f"{days_of_week[day - 1]}       {week_type}\n{teacher_name}\n\n"
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x["time"]))
        for lesson in sorted_lessons:
            subject = re.sub(r"\([^)]*\)", "", lesson["subject"])
            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", lesson["subject"])))
            text += f"👨🏻‍💻 {lesson['schedule_id']}\n" if editing else ""
            text += (
                f"{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n"
                f"📖 {subject}\n"
            )
            try:
                text += f"👫 {lesson['group']}\n"
            except KeyError:
                text += f"👨‍🏫 {lesson['teacher']}\n"
            text += f"🏠 Ауд. {lesson['room']}\n\n"
        return text
    else:
        return f"{header}Сегодня пар нет!"


@sql_kit(config.SCHEDULE_DB)
def get_room_schedule(day, week, room_name, editing: bool = False, cursor: sqlite3.Cursor = None):
    """Возвращает отформатированное расписание для указанной аудитории на указанный день и неделю. Если аудитория имеет несколько вариантов (например, 2-13М и 2-13аМ), то возвращает расписание для всех вариантов."""

    from app.misc import get_lesson_label, get_time_symbol, time_to_minutes

    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Понедельник",
    ]

    if room_name[:-1] == "2-13":
        room_variants = [room_name[:-1] + variant for variant in ["М", "аМ", "бМ"]]
    elif room_name[:-1] == "3-15":
        room_variants = [room_name[:-1] + variant for variant in ["К", "аК", "бК"]]
    else:
        room_variants = [room_name]

    query = f"""
        SELECT GROUP_CONCAT(s.ScheduleID, ', '), s.Time, sub.SubjectName, GROUP_CONCAT(g.GroupName, ', ') AS GroupNames, t.TeacherName
        FROM (
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM Schedule
            UNION ALL
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM CollegeSchedule
        ) s            
        JOIN Subjects sub ON s.SubjectID = sub.SubjectID
        JOIN Groups g ON s.GroupID = g.GroupID
        JOIN Rooms r ON s.RoomID = r.RoomID
        JOIN Teachers t ON s.TeacherID = t.TeacherID
        WHERE s.DayOfWeek = ? AND s.WeekType = ? AND r.RoomName = ?
        GROUP BY s.Time, sub.SubjectName, t.TeacherName
        ORDER BY s.Time
        """

    schedule = []
    for room in room_variants:
        cursor.execute(query, (days_of_week[day - 1], week_type, room))
        rows = cursor.fetchall()

        for row in rows:
            schedule_id, time, subject, group, teacher = row
            schedule.append(
                {
                    "schedule_id": schedule_id,
                    "time": time,
                    "subject": subject,
                    "group": group,
                    "teacher": teacher,
                    "room": room,
                }
            )
    text = header = f"{days_of_week[day - 1]}       {week_type}\n{room_name}\n\n"
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x["time"]))
        for lesson in sorted_lessons:
            subject = re.sub(r"\([^)]*\)", "", lesson["subject"])
            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", lesson["subject"])))
            suffix = re.sub(r"\d*-\d*", "", lesson["room"])
            suffix = f"|{suffix[:-1]}|" if suffix[:-1] != "" else ""
            text += f"👨🏻‍💻 {lesson['schedule_id']}\n" if editing else ""
            text += (
                f"{get_time_symbol(lesson['time'])}{lesson['time']}    {suffix}   {label}\n"
                f"📖 {subject}\n"
                f"👫 {lesson['group']}\n"
                f"‍👨‍🏫 {lesson['teacher']}\n\n"
            )
        return text
    else:
        return f"{header}Сегодня пар нет!"
