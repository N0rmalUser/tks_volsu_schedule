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

from app.config import ALIASES, SCHEDULE_DB, STUDENTS
from app.database import sql_kit


@sql_kit(SCHEDULE_DB)
def get_group_schedule(day: int, week: int, group_name: str, cursor: sqlite3.Cursor = None) -> str:
    """Возвращает отформатированное расписание для указанной группы на указанный день и неделю"""

    from app.misc import get_lesson_label, get_time_symbol, time_to_minutes

    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    query = """
        SELECT
            GROUP_CONCAT(s.ScheduleID, ', '),
            s.Time, sub.SubjectName,
            r.RoomName,
            t.TeacherName,
            Subgroup
        FROM (
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType, Subgroup
            FROM Schedule
            UNION ALL
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType, 0 AS Subgroup
            FROM CollegeSchedule
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
        schedule_id, time, subject, room_name, teacher, subgroup = row
        schedule.append(
            {
                "schedule_id": schedule_id,
                "time": time,
                "subject": subject,
                "room": room_name,
                "teacher": teacher,
                "subgroup": subgroup,
            }
        )
    text = header = f"{days_of_week[day - 1]}       {week_type}\n{group_name}\n\n"
    if schedule:
        sorted_lessons = sorted(
            schedule,
            key=lambda x: (
                time_to_minutes(x["time"]),
                0 if x.get("subgroup", 0) == 0 else x["subgroup"],
            ),
        )
        for lesson in sorted_lessons:
            subject = re.sub(r"\([^)]*\)", "", lesson["subject"])

            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", lesson["subject"])))
            text += (
                f"{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n"
                f"📖 {subject}\n"
                f"{f'👫 Подгруппа: {lesson["subgroup"]}\n' if lesson['subgroup'] else ''}"
                f"👨‍🏫 {lesson['teacher']}\n"
                f"🏠 Ауд. {lesson['room']}\n\n"
            )
        return text
    else:
        return f"{header}Сегодня пар нет!"


@sql_kit(SCHEDULE_DB)
def get_teacher_schedule(day: int, week: int, teacher_name: str, cursor: sqlite3.Cursor = None) -> str:
    """Возвращает отформатированное расписание для указанного преподавателя на указанный день и неделю. Если
    преподаватель обучается в какой-либо группе (указывается в config.py), то возвращает расписание для этой группы,
    смешанное с расписанием преподавателя."""

    from app.misc import get_lesson_label, get_time_symbol, time_to_minutes

    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    schedule = []
    if teacher_name in STUDENTS.keys():
        query = """
                SELECT
                    s.ScheduleID,
                    s.Time,
                    sub.SubjectName,
                    r.RoomName,
                    t.TeacherName
                FROM (
                    SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType, Subgroup
                    FROM Schedule
                    UNION ALL
                    SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType, 0 AS Subgroup
                    FROM CollegeSchedule
                ) s
                JOIN Subjects sub ON s.SubjectID = sub.SubjectID
                JOIN Groups g ON s.GroupID = g.GroupID
                JOIN Rooms r ON s.RoomID = r.RoomID
                JOIN Teachers t ON s.TeacherID = t.TeacherID
                WHERE g.GroupName = ? AND Subgroup IN ({}) AND s.DayOfWeek = ? AND s.WeekType = ?
                ORDER BY s.Time;
                """

        if "." in STUDENTS[teacher_name]:
            group, subgroup = STUDENTS[teacher_name].split(".")
            subgroup_list = [0] + [int(s) for s in subgroup.split(",") if s.isdigit()]

        else:
            group = STUDENTS[teacher_name]
            subgroup_list = [0]
        placeholders = ", ".join("?" for _ in subgroup_list)
        query = query.format(placeholders)
        params = [group] + subgroup_list + [days_of_week[day - 1], week_type]
        cursor.execute(query, params)
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

    teacher_variants = [teacher_name]
    if teacher_name in ALIASES:
        teacher_variants.extend(ALIASES[teacher_name])

    query = f"""
            SELECT
                GROUP_CONCAT(s.ScheduleID, ', '),
                s.Time,
                sub.SubjectName,
                GROUP_CONCAT(g.GroupName, ', ')
                AS GroupNames, r.RoomName, Subgroup
            FROM (
                SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, GroupID, RoomID, TeacherID, Subgroup
                FROM Schedule
                UNION ALL
                SELECT ScheduleID, Time, DayOfWeek, WeekType, SubjectID, GroupID, RoomID, TeacherID, 0 AS Subgroup
                FROM CollegeSchedule
            ) s
            JOIN Subjects sub ON s.SubjectID = sub.SubjectID
            JOIN Groups g ON s.GroupID = g.GroupID
            JOIN Rooms r ON s.RoomID = r.RoomID
            JOIN Teachers t ON s.TeacherID = t.TeacherID
            WHERE t.TeacherName IN ({", ".join("?" for _ in teacher_variants)}) AND s.DayOfWeek = ? AND s.WeekType = ?
            GROUP BY s.Time, sub.SubjectName, r.RoomName
            ORDER BY s.Time
            """
    cursor.execute(query, teacher_variants + [days_of_week[day - 1], week_type])
    rows = cursor.fetchall()
    for row in rows:
        schedule_id, time, subject, group, room_name, subgroup = row
        schedule.append(
            {
                "schedule_id": schedule_id,
                "time": time,
                "subject": subject,
                "group": group,
                "room": room_name,
                "subgroup": subgroup,
            }
        )
    text = header = f"{days_of_week[day - 1]}       {week_type}\n{teacher_name}\n\n"
    if schedule:
        sorted_lessons = sorted(
            schedule,
            key=lambda x: (
                time_to_minutes(x["time"]),
                0 if x.get("subgroup", 0) == 0 else x["subgroup"],
            ),
        )

        for lesson in sorted_lessons:
            subject = re.sub(r"\([^)]*\)", "", lesson["subject"])
            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", lesson["subject"])))
            text += f"{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n"
            try:
                text += f"👫 {f'{lesson["group"]}.{lesson["subgroup"]}' if lesson['subgroup'] else lesson['group']}\n"
            except KeyError:
                text += f"👨‍🏫 {lesson['teacher']}\n"
            text += f"🏠 Ауд. {lesson['room']}\n\n"
        return text
    else:
        return f"{header}Сегодня пар нет!"


@sql_kit(SCHEDULE_DB)
def get_room_schedule(day: int, week: int, room_name: str, cursor: sqlite3.Cursor = None) -> str:
    """Возвращает отформатированное расписание для указанной аудитории на указанный день и неделю. Если аудитория
    имеет несколько вариантов (например, 2-13М и 2-13аМ), то возвращает расписание для всех вариантов."""

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

    query = """
        SELECT
            GROUP_CONCAT(s.ScheduleID, ', '),
            s.Time,
            sub.SubjectName,
            GROUP_CONCAT(g.GroupName, ', ')
            AS GroupNames, t.TeacherName, Subgroup
        FROM (
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType, Subgroup
            FROM Schedule
            UNION ALL
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType, 0 AS Subgroup
            FROM CollegeSchedule
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
            schedule_id, time, subject, group, teacher, subgroup = row
            schedule.append(
                {
                    "schedule_id": schedule_id,
                    "time": time,
                    "subject": subject,
                    "group": group,
                    "teacher": teacher,
                    "room": room,
                    "subgroup": subgroup,
                }
            )
    text = header = f"{days_of_week[day - 1]}       {week_type}\n{room_name}\n\n"
    if schedule:
        sorted_lessons = sorted(
            schedule,
            key=lambda x: (
                time_to_minutes(x["time"]),
                0 if x.get("subgroup", 0) == 0 else x["subgroup"],
            ),
        )
        for lesson in sorted_lessons:
            subject = re.sub(r"\([^)]*\)", "", lesson["subject"])
            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", lesson["subject"])))
            suffix = re.sub(r"\d*-\d*", "", lesson["room"])
            suffix = f"|{suffix[:-1]}|" if suffix[:-1] != "" else ""
            text += (
                f"{get_time_symbol(lesson['time'])}{lesson['time']}    {suffix}   {label}\n"
                f"📖 {subject}\n"
                f"👫 {f'{lesson["group"]}.{lesson["subgroup"]}' if lesson['subgroup'] else lesson['group']}\n"
                f"‍👨‍🏫 {lesson['teacher']}\n\n"
            )
        return text
    else:
        return f"{header}Сегодня пар нет!"
