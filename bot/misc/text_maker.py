import config

import re

import sqlite3


def time_to_minutes(time_str: str) -> int:
    """
    Method for converting time from string to minutes
    :param time_str:  :call_type: str
    :return:  :rtype: int
    """
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def get_time_symbol(start_time: str) -> str:
    """
    Method for getting time symbol by start time
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
    Method for getting lesson label by bad label from schedule
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


def get_group_schedule(day, week, group_name):
    conn = sqlite3.connect(config.SCHEDULE_PATH)
    cursor = conn.cursor()

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
    conn.close()

    text = header = f'{days_of_week[day - 1]}       {week_type}\n{group_name}\n'
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x['time']))
        for lesson in sorted_lessons:
            subject = re.sub(r'\([^)]*\)', '', lesson['subject'])
            label = get_lesson_label(str(re.search(r'\(([^)]*)\)', lesson['subject'])))
            text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👨‍🏫 {lesson['teacher']}\n🏠 Ауд. {lesson['room']}\n"
        return text
    else:
        status = 'Сегодня пар нет!'
        return f'{header}\n\n{status}'


def get_teacher_schedule(day, week, teacher_name):
    conn = sqlite3.connect(config.SCHEDULE_PATH)
    cursor = conn.cursor()

    week_type = "Числитель" if week == 1 else "Знаменатель"
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    query = """
    SELECT s.Time, sub.SubjectName, g.GroupName, r.RoomNumber
    FROM Schedule s
    JOIN Subjects sub ON s.SubjectID = sub.SubjectID
    JOIN Groups g ON s.GroupID = g.GroupID
    JOIN Rooms r ON s.RoomID = r.RoomID
    JOIN Teachers t ON s.TeacherID = t.TeacherID
    WHERE t.TeacherName = ? AND s.DayOfWeek = ? AND s.WeekType = ?
    ORDER BY s.Time
    """

    cursor.execute(query, (teacher_name, days_of_week[day - 1], week_type))
    rows = cursor.fetchall()

    schedule = []
    for row in rows:
        time, subject, group, teacher_name = row
        schedule.append({
            "time": time,
            "subject": subject,
            "group": group,
            "room": teacher_name
        })

    conn.close()

    text = header = f'{days_of_week[day - 1]}       {week_type}\n{teacher_name}\n'
    if schedule:
        sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x['time']))
        for lesson in sorted_lessons:
            subject = re.sub(r'\([^)]*\)', '', lesson['subject'])
            label = get_lesson_label(str(re.search(r'\(([^)]*)\)', lesson['subject'])))
            text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👫 {lesson['group']}\n🏠 Ауд. {lesson['room']}\n"
        return text
    else:
        status = 'Сегодня пар нет!'
        return f'{header}\n\n{status}'


def get_room_schedule(day, week, room_name):
    conn = sqlite3.connect(config.SCHEDULE_PATH)
    cursor = conn.cursor()

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

    conn.close()

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
