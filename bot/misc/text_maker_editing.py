from bot.database.utils import sql_kit
from bot.misc.text_maker import (
    time_to_minutes,
    get_time_symbol,
    get_lesson_label,
    get_date_for_day,
)
import config
import re
import sqlite3


@sql_kit(config.SCHEDULE_DB)
def get_teacher_schedule(
    day: int, week: int, teacher_name: str, cursor: sqlite3.Cursor
):
    """Возвращает отформатированное расписание для указанного преподавателя на указанный день и неделю. Если преподаватель обучается в какой-либо группе (указывается в config.py), то возвращает расписание для этой группы, смешанное с расписанием преподавателя."""

    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    schedule = []
    if teacher_name in config.special_teachers.keys():

        query = """
            SELECT s.ScheduleID, s.Time, sub.SubjectName, r.RoomNumber, t.TeacherName
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
            schedule_id, time, subject, room_number, teacher = row
            schedule.append(
                {
                    "schedule_id": schedule_id,
                    "time": time,
                    "subject": subject,
                    "room": room_number,
                    "teacher": teacher,
                }
            )

    query = """
        SELECT GROUP_CONCAT(s.ScheduleID, ', '), s.Time, sub.SubjectName, GROUP_CONCAT(g.GroupName, ', ') AS GroupNames, r.RoomNumber
        FROM (
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM Schedule
            UNION ALL
            SELECT ScheduleID, Time, SubjectID, GroupID, RoomID, TeacherID, DayOfWeek, WeekType FROM CollegeSchedule
        ) s
        JOIN Subjects sub ON s.SubjectID = sub.SubjectID
        JOIN Groups g ON s.GroupID = g.GroupID
        JOIN Rooms r ON s.RoomID = r.RoomID
        JOIN Teachers t ON s.TeacherID = t.TeacherID
        WHERE t.TeacherName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
        GROUP BY s.Time, sub.SubjectName, t.TeacherName, r.RoomNumber
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
    text = header = f"{days_of_week[day - 1]}       {week_type}\n{teacher_name}\n"
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x["time"]))
        for lesson in sorted_lessons:
            subject = re.sub(r"\([^)]*\)", "", lesson["subject"])
            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", lesson["subject"])))
            try:
                text += f"\n👨🏻‍💻 {lesson['schedule_id']}\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👫 {lesson['group']}\n🏠 Ауд. {lesson['room']}\n"
            except KeyError:
                text += f"\n👨🏻‍💻 {lesson['schedule_id']}\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👨‍🏫 {lesson['teacher']}\n🏠 Ауд. {lesson['room']}\n"
        text += f"\nДата: {date}"
        return text
    else:
        return f"{header}\nСегодня пар нет!\n\nДата: {date}"
