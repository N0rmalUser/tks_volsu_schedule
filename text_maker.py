from data import config
import dbUtils

import re


def get_group_schedule(user_id: int) -> str:
    """
    Method for getting schedule for group by user_id from schedule in json format
    :param user_id:  :type: int
    :return:  :rtype: str
    """
    week, day, group_name = weeks[dbUtils.get_week(user_id)], days[dbUtils.get_day(user_id)], dbUtils.get_group(user_id)
    data = config.schedule

    text = header = f'{day}       {week}\n{group_name}\n'
    for group in data['groups']:
        if group['group'] == group_name:
            schedule = group['weeks'].get(week, {}).get(day)
            if not schedule:
                status = 'На этой неделе пар нет!' if week not in group['weeks'] else 'Сегодня пар нет!'
                return f'{header}\n{status}'

            sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x['time']))

            for lesson in sorted_lessons:
                subject = re.sub(r'\([^)]*\)', '', lesson['subject'])
                label = get_lesson_label(str(re.search(r'\(([^)]*)\)', lesson['subject'])))
                text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👨‍🏫 {lesson['teacher']}\n🏠 Ауд. {lesson['room']}\n"
            return text
    return f'{header}\n\nИнформация о группе не найдена!'


def get_teacher_schedule(user_id: int) -> str:
    """
    Method for getting schedule for teacher by user_id from schedule in json format
    :param user_id:  :type: int
    :return:  :rtype: str
    """
    week, day, teacher_name = weeks[dbUtils.get_week(user_id)], days[dbUtils.get_day(user_id)], dbUtils.get_teacher(user_id)
    data = config.schedule

    text = header = f'{day}       {week}\n{teacher_name}\n'
    for teacher in data['teachers']:
        if teacher['teacher'] == teacher_name:
            schedule = teacher['weeks'].get(week, {}).get(day)
            if not schedule:
                status = 'На этой неделе пар нет!' if week not in teacher['weeks'] else 'Сегодня пар нет!'
                return f'{header}\n{status}'

            sorted_lessons = sorted(schedule, key=lambda x: time_to_minutes(x['time']))

            for lesson in sorted_lessons:
                subject = re.sub(r'\([^)]*\)', '', lesson['subject'])
                label = get_lesson_label(str(re.search(r'\(([^)]*)\)', lesson['subject'])))
                text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👫{lesson['group']}\n🏠Ауд. {lesson['room']}\n"
            return text
    return f'{header}\n\nИнформация о преподавателе не найдена!'


def get_room_schedule(user_id: int) -> str:
    """
    Method for getting schedule for room by user_id from schedule in json format
    :param user_id:  :type: int
    :return:  :rtype: str
    """
    week, day, room_name = weeks[dbUtils.get_week(user_id)], days[dbUtils.get_day(user_id)], rooms[dbUtils.get_room(user_id)]
    data = config.schedule
    room_variants = [room_name + variant for variant in ['М', 'аМ', 'бМ']] if room_name == '2-13' else [room_name + variant for variant in ['К', 'аК', 'бК']] if room_name == '3-15' else [room_name]

    lesson_dict = {}
    header = f'{day}       {week}\n{room_name}\n'

    schedule_found = False
    no_classes_for_week = True
    no_classes_for_day = True

    for room_variant in room_variants:
        for room in data['rooms']:
            if room['room'] == room_variant or (room['room'].startswith(room_variant[:-1]) and (room['room'].endswith('М') or room['room'].endswith('К'))):
                schedule = room['weeks'].get(week, {}).get(day)
                if schedule:
                    schedule_found = True
                    no_classes_for_day = False
                    for lesson in schedule:
                        lesson_key = (lesson['time'], lesson['subject'], lesson['teacher'])
                        if lesson_key not in lesson_dict:
                            lesson_dict[lesson_key] = lesson
                            lesson_dict[lesson_key]['groups'] = [lesson['group']]
                        else:
                            lesson_dict[lesson_key]['groups'].append(lesson['group'])
                elif week in room['weeks']:
                    no_classes_for_week = False

    if not schedule_found:
        if no_classes_for_week:
            status = 'На этой неделе пар нет!'
        elif no_classes_for_day:
            status = 'Сегодня пар нет!'
        return f'{header}\n{status}'

    if not lesson_dict:
        return f'{day}       {week}\n{room_name}\n\nИнформация о кабинете не найдена!'

    sorted_lessons = sorted(lesson_dict.values(), key=lambda x: time_to_minutes(x['time']))
    text = header
    for lesson in sorted_lessons:
        subject = re.sub(r'\([^)]*\)', '', lesson['subject'])
        label = get_lesson_label(str(re.search(r'\(([^)]*)\)', lesson['subject'])))
        group_list = ', '.join(lesson['groups'])
        text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}       {label}\n📖 {subject}\n👫 {group_list}\n‍👨‍🏫 {lesson['teacher']}\n"

    return text


def get_lesson_label(subject: str) -> str:
    """
    Method for getting lesson label by bad label from schedule
    :param subject:  :type: str
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


def time_to_minutes(time_str: str) -> int:
    """
    Method for converting time from string to minutes
    :param time_str:  :type: str
    :return:  :rtype: int
    """
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def get_time_symbol(start_time: str) -> str:
    """
    Method for getting time symbol by start time
    :param start_time:  :type: str
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


days = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Понедельник"
}
weeks = {
    1: "Числитель",
    2: "Знаменатель"
}
rooms = {
    "1-19m": "1-19М",
    "2-01k": "2-01К",
    "2-06m": "2-06М",
    "2-13m": "2-13М",
    "2-17m": "2-17М",
    "3-15k": "3-15К",
    "3-16k": "3-16К",
}
