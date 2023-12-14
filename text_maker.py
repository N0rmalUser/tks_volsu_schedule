import utils


def get_group_schedule(week, day, group_name):
    week, day = utils.weeks[week], utils.days[day]
    data = utils.group_json

    group_schedule = None
    for group in data['groups']:
        if group['group'] == group_name:
            group_schedule = group
            break

    if week not in group_schedule['weeks']:
        return f"{day}  {week}\n{group_name}\n\nНа этой неделе пар нет!"

    if day not in group_schedule['weeks'][week]:
        return f"{day}  {week}\n{group_name}\n\nСегодня пар нет!"

    lessons = group_schedule['weeks'][week][day]
    sorted_lessons = sorted(lessons, key=lambda x: time_to_minutes(x['time']))

    text = f"{day}  {week}\n{group_name}\n"
    for lesson in sorted_lessons:
        text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}\n📖{lesson['subject']}\n👨‍🏫{lesson['teacher']}\n🏠Ауд. {lesson['room']}\n"

    return text


def get_teacher_schedule(week, day, teacher_name):
    week, day = utils.weeks[week], utils.days[day]
    data = utils.teacher_json

    teacher_schedule = None
    for teacher in data['teachers']:
        if teacher['teacher'] == teacher_name:
            teacher_schedule = teacher
            break

    if week not in teacher_schedule['weeks']:
        return f"{day}  {week}\n{teacher_name}\n\nНа этой неделе пар нет!"

    if day not in teacher_schedule['weeks'][week]:
        return f"{day}\nПреподаватель: {teacher_name}\n\nСегодня пар нет!!"

    lessons = teacher_schedule['weeks'][week][day]
    sorted_lessons = sorted(lessons, key=lambda x: time_to_minutes(x['time']))

    text = f"{day}\nПреподаватель: {teacher_name}\n"
    for lesson in sorted_lessons:
        text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}\n📖{lesson['subject']}\n👫{lesson['group']}\n🏠Ауд. {lesson['room']}\n"

    return text


def get_room_schedule(week, day, room_name):
    week, day, room_name = utils.weeks[week], utils.days[day], utils.rooms[room_name]
    data = utils.room_json

    room_schedule = None
    for room in data['rooms']:
        if room['room'] == room_name:
            room_schedule = room
            break

    if week not in room_schedule['weeks']:
        return f"{day}  {week}\n{room_name}\n\nНа этой неделе пар нет!"

    if day not in room_schedule['weeks'][week]:
        return f"{day}  {week}\n{room_name}\n\nСегодня пар нет!"

    lessons = room_schedule['weeks'][week][day]
    sorted_lessons = sorted(lessons, key=lambda x: time_to_minutes(x['time']))

    text = f"{day}  {week}\n{room_name}\n"
    for lesson in sorted_lessons:
        text += f"\n{get_time_symbol(lesson['time'])}{lesson['time']}\n📖{lesson['subject']}\n👫{lesson['group']}\n‍👨‍🏫{lesson['teacher']}\n"

    return text


def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def get_time_symbol(start_time):
    hour = int(start_time.split(':')[0])
    if 8 <= hour < 10:
        return "🕣"
    elif 10 <= hour < 12:
        return "🕙"
    elif 12 <= hour < 13:
        return "🕛"
    elif 13 <= hour < 14:
        return "🕜"
    elif 14 <= hour < 16:
        return "🕞"
    elif 16 <= hour < 18:
        return "🕔"
    elif 18 <= hour < 20:
        return "🕡"
    else:
        return "🕙"
