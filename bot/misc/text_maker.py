import config

import re

from bot.misc.utils import sql_kit

import sqlite3


def time_to_minutes(time_str: str) -> int:
    """
    Метод для перевода времени в минуты
    :param time_str:  :call_type: str
    :return:  :rtype: int
    """
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def get_time_symbol(start_time: str) -> str:
    """
    Метод для получения эмодзи часов с указанным временем времени
    :param start_time:  :call_type: str
    :return:  :rtype: str
    """
    hour = int(start_time.split(':')[0])
    if 8 <= hour < 10:
        return '🕣 '
    elif 10 <= hour < 12:
        return '🕙 '
    elif 12 <= hour < 13:
        return '🕛 '
    elif 13 <= hour < 14:
        return '🕜 '
    elif 14 <= hour < 16:
        return '🕞 '
    elif 16 <= hour < 18:
        return '🕔 '
    elif 18 <= hour < 20:
        return '🕡 '
    else:
        return '🕙 '


def get_lesson_label(subject: str) -> str:
    """
    Метод для получения типа пары по его сокращени
    :param subject:  :call_type: str
    :return:  :rtype: str
    """
    if 'Пр' in subject:
        return 'Практика'
    elif 'пр' in subject:
        return 'Практика'
    elif 'Пр.' in subject:
        return 'Практика'
    elif 'пр.' in subject:
        return 'Практика'
    elif 'Лаб' in subject:
        return 'Лабораторные'
    elif 'лаб' in subject:
        return 'Лабораторные'
    elif 'Лаб.' in subject:
        return 'Лабораторные'
    elif 'лаб.' in subject:
        return 'Лабораторные'
    elif 'Л' in subject:
        return 'Лекция'
    elif 'л' in subject:
        return 'Лекция'
    elif 'Л.' in subject:
        return 'Лекция'
    elif 'л.' in subject:
        return 'Лекция'
    elif 'кур/проект' in subject:
        return 'Курсовой проект'
    elif 'кур/проек.' in subject:
        return 'Курсовой проект'
    else:
        return ''


@sql_kit(config.SCHEDULE_DB)
def get_group_schedule(day: int, week: int, group_name: str, cursor: sqlite3.Cursor):
    """Возвращает отформатированное расписание для указанной группы на указанный день и неделю"""
    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    query = """
        SELECT s.Time, sub.SubjectName, r.RoomNumber, t.TeacherName
        FROM Schedule s
        JOIN Subjects sub ON s.SubjectID = sub.SubjectID
        JOIN Groups g ON s.GroupID = g.GroupID
        JOIN Rooms r ON s.RoomID = r.RoomID
        JOIN Teachers t ON s.TeacherID = t.TeacherID
        WHERE g.GroupName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
        ORDER BY s.Time
        """

    cursor.execute(query, (group_name, days_of_week[day - 1], week_type))
    rows = cursor.fetchall()

    schedule = []
    for row in rows:
        time, subject, room_number, teacher = row
        schedule.append({
            "time": time,
            "subject": subject,
            "room": room_number,
            "teacher": teacher
        })

    text = header = f'{days_of_week[day - 1]}       {week_type}\n{group_name}\n'
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x['time']))
        for lesson in sorted_lessons:
            subject = re.sub(r'\([^)]*\)', '', lesson['subject'])
            label = get_lesson_label(str(re.search(r'\(([^)]*)\)', lesson['subject'])))
            text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👨‍🏫 {lesson['teacher']}\n🏠 Ауд. {lesson['room']}\n"
        return text
    else:
        return f'{header}\n\nСегодня пар нет!'


@sql_kit(config.SCHEDULE_DB)
def get_teacher_schedule(day: int, week: int, teacher_name: str, cursor: sqlite3.Cursor):
    """Возвращает отформатированное расписание для указанного преподавателя на указанный день и неделю. Если преподаватель обучается в какой-либо группе (указывается в config.py), то возвращает расписание для этой группы, смешанное с расписанием преподавателя."""
    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    schedule = []
    if teacher_name in config.special_teachers.keys():

        query = """
                SELECT s.Time, sub.SubjectName, r.RoomNumber, t.TeacherName
                FROM Schedule s
                JOIN Subjects sub ON s.SubjectID = sub.SubjectID
                JOIN Groups g ON s.GroupID = g.GroupID
                JOIN Rooms r ON s.RoomID = r.RoomID
                JOIN Teachers t ON s.TeacherID = t.TeacherID
                WHERE g.GroupName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
                ORDER BY s.Time
                """

        cursor.execute(query, (config.special_teachers[teacher_name], days_of_week[day - 1], week_type))
        rows = cursor.fetchall()
        for row in rows:
            time, subject, room_number, teacher = row
            schedule.append({
                "time": time,
                "subject": subject,
                "room": room_number,
                "teacher": teacher
            })

    query = """
        SELECT s.Time, sub.SubjectName, GROUP_CONCAT(g.GroupName, ', ') AS GroupNames, r.RoomNumber
        FROM Schedule s
        JOIN Subjects sub ON s.SubjectID = sub.SubjectID
        JOIN Groups g ON s.GroupID = g.GroupID
        JOIN Rooms r ON s.RoomID = r.RoomID
        JOIN Teachers t ON s.TeacherID = t.TeacherID
        WHERE t.TeacherName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
        GROUP BY s.Time, sub.SubjectName, r.RoomNumber
        ORDER BY s.Time
        """

    cursor.execute(query, (teacher_name, days_of_week[day - 1], week_type))
    rows = cursor.fetchall()

    for row in rows:
        time, subject, group, room_name = row
        schedule.append({
            "time": time,
            "subject": subject,
            "group": group,
            "room": room_name
        })

    text = header = f'{days_of_week[day - 1]}       {week_type}\n{teacher_name}\n'
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x['time']))
        for lesson in sorted_lessons:
            subject = re.sub(r'\([^)]*\)', '', lesson['subject'])
            label = get_lesson_label(str(re.search(r'\(([^)]*)\)', lesson['subject'])))
            try:
                text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👫 {lesson['group']}\n🏠 Ауд. {lesson['room']}\n"
            except KeyError:
                text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👨‍🏫 {lesson['teacher']}\n🏠 Ауд. {lesson['room']}\n"
        return text
    else:
        status = 'Сегодня пар нет!'
        return f'{header}\n\n{status}'


@sql_kit(config.SCHEDULE_DB)
def get_room_schedule(day, week, room_name, cursor: sqlite3.Cursor):
    """Возвращает отформатированное расписание для указанной аудитории на указанный день и неделю. Если аудитория имеет несколько вариантов (например, 2-13М и 2-13аМ), то возвращает расписание для всех вариантов."""
    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Понедельник"]

    if room_name[:-1] == '2-13':
        room_variants = [room_name[:-1] + variant for variant in ['М', 'аМ', 'бМ']]
    elif room_name[:-1] == '3-15':
        room_variants = [room_name[:-1] + variant for variant in ['К', 'аК', 'бК']]
    else:
        room_variants = [room_name]

    schedule = []
    for room in room_variants:
        query = f"""
            SELECT s.Time, sub.SubjectName, GROUP_CONCAT(g.GroupName, ', ') AS GroupNames, t.TeacherName
            FROM Schedule s
            JOIN Subjects sub ON s.SubjectID = sub.SubjectID
            JOIN Groups g ON s.GroupID = g.GroupID
            JOIN Rooms r ON s.RoomID = r.RoomID
            JOIN Teachers t ON s.TeacherID = t.TeacherID
            WHERE s.DayOfWeek = ? AND s.WeekType = ? AND r.RoomNumber = ?
            GROUP BY s.Time, sub.SubjectName, t.TeacherName
            ORDER BY s.Time
            """

        cursor.execute(query, (days_of_week[day - 1], week_type, room))
        rows = cursor.fetchall()

        for row in rows:
            time, subject, group, teacher = row
            schedule.append({
                "time": time,
                "subject": subject,
                "group": group,
                "teacher": teacher,
                "room": room
            })

    text = header = f'{days_of_week[day - 1]}       {week_type}\n{room_name}\n'
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x['time']))
        for lesson in sorted_lessons:
            subject = re.sub(r'\([^)]*\)', '', lesson['subject'])
            label = get_lesson_label(str(re.search(r'\(([^)]*)\)', lesson['subject'])))
            suffix = re.sub(r'\d*-\d*', '', lesson['room'])
            suffix = f'|{suffix[:-1]}|' if suffix[:-1] != '' else ''
            text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}    {suffix}   {label}\n📖 {subject}\n👫 {lesson['group']}\n‍👨‍🏫 {lesson['teacher']}\n"
        return text
    else:
        status = 'Сегодня пар нет!'
        return f'{header}\n\n{status}'
