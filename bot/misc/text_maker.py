import re
import sqlite3

import config
from bot.database.utils import sql_kit


def time_to_minutes(time_str: str) -> int:
    """Метод для перевода времени в минуты"""

    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes


def get_time_symbol(start_time: str) -> str:
    """Метод для получения эмодзи часов с указанным временем времени"""

    hour = int(start_time.split(":")[0])
    if 8 <= hour < 10:
        return "🕣 "
    elif 10 <= hour < 12:
        return "🕙 "
    elif 12 <= hour < 13:
        return "🕛 "
    elif 13 <= hour < 14:
        return "🕜 "
    elif 14 <= hour < 16:
        return "🕞 "
    elif 16 <= hour < 18:
        return "🕔 "
    elif 18 <= hour < 20:
        return "🕡 "
    else:
        return "🕙 "


def get_lesson_label(subject: str) -> str:
    """Метод для получения типа пары по его сокращению"""

    if "пр" in subject.lower():
        return "Практика"
    elif "пр." in subject.lower():
        return "Практика"
    elif "лаб" in subject.lower():
        return "Лабораторные"
    elif "лаб." in subject.lower():
        return "Лабораторные"
    elif "л" in subject.lower():
        return "Лекция"
    elif "л." in subject.lower():
        return "Лекция"
    elif ("курс" or "кур/проект" or "кур/проек.") in subject.lower():
        return "Курсовой проект"
    else:
        return ""


def get_date_for_day(day: int, week: int) -> str:
    """Возвращает дату для указанного дня недели и типа недели. Если указан день недели, который уже прошел в этой неделе, то возвращает дату для следующей недели. Если сегодня числитель, но целевой день на знаменателе, то возвращает дату для следующей недели."""

    from datetime import datetime, timedelta

    today = datetime.now()
    today_day_of_week = today.weekday() + 1
    day_diff = day - today_day_of_week

    if day_diff < 0 or (
        day_diff == 0 and week == 2 and today.isocalendar()[1] % 2 == week
    ):
        day_diff += 7
    if today.isocalendar()[1] % 2 == 1 and week == 2:
        day_diff += 7

    return (today + timedelta(days=day_diff)).strftime("%d.%m.%Y")


@sql_kit(config.SCHEDULE_DB)
def get_group_schedule(
    day: int,
    week: int,
    group_name: str,
    editing: bool = False,
    cursor: sqlite3.Cursor = None,
):
    """Возвращает отформатированное расписание для указанной группы на указанный день и неделю"""
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
    # FIXME: Вчерашняя дата показывается как через неделю
    date = get_date_for_day(day, week)
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
        text += f"Дата: {date}"
        return text
    else:
        return f"{header}Сегодня пар нет!\n\nДата: {date}"


@sql_kit(config.SCHEDULE_DB)
def get_teacher_schedule(
    day: int,
    week: int,
    teacher_name: str,
    editing: bool = False,
    cursor: sqlite3.Cursor = None,
):
    """Возвращает отформатированное расписание для указанного преподавателя на указанный день и неделю. Если преподаватель обучается в какой-либо группе (указывается в config.py), то возвращает расписание для этой группы, смешанное с расписанием преподавателя."""

    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    schedule = []
    if teacher_name in config.special_teachers.keys():

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
            (config.special_teachers[teacher_name], days_of_week[day - 1], week_type),
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
        SELECT GROUP_CONCAT(s.ScheduleID, ', '), s.Time, sub.SubjectName, GROUP_CONCAT(g.GroupName) AS GroupNames, r.RoomName
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
    date = get_date_for_day(day, week)
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
        text += f"Дата: {date}"
        return text
    else:
        return f"{header}Сегодня пар нет!\n\nДата: {date}"


@sql_kit(config.SCHEDULE_DB)
def get_room_schedule(
    day, week, room_name, editing: bool = False, cursor: sqlite3.Cursor = None
):
    """Возвращает отформатированное расписание для указанной аудитории на указанный день и неделю. Если аудитория имеет несколько вариантов (например, 2-13М и 2-13аМ), то возвращает расписание для всех вариантов."""
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

    schedule = []
    for room in room_variants:
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

    date = get_date_for_day(day, week)
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
        text += f"Дата: {date}"
        return text
    else:
        return f"{header}Сегодня пар нет!\n\nДата: {date}"
