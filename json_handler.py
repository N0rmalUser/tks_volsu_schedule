import json

import utils


def wrap_text(text):
    max_len = 28
    if len(text) > max_len:
        space_index = max(text.rfind(' ', max_len-6, max_len-2), max_len-2)
        text = text[:space_index] + "\n" + text[space_index:]
    if len(text) > max_len * 2:
        text = text[:max_len * 2 - 10] + "... " + text[-4:]
    return text


def get_teacher_schedule(week: str, day: str, teacher_name: str):
    schedule_template = [
        {"time": "8:30", "subject": "", "room": "", "group": ""},
        {"time": "10:10", "subject": "", "room": "", "group": ""},
        {"time": "12:00", "subject": "", "room": "", "group": ""},
        {"time": "13:40", "subject": "", "room": "", "group": ""},
        {"time": "15:20", "subject": "", "room": "", "group": ""},
        {"time": "17:00", "subject": "", "room": "", "group": ""},
        {"time": "18:40", "subject": "", "room": "", "group": ""}
    ]

    for teacher in utils.teacher_json['teachers']:
        if teacher['teacher'] == teacher_name:
            weeks_data = teacher.get('weeks', {})
            day_schedule = weeks_data.get(week, {}).get(day, None)
            if day_schedule is None:
                return None

            for class_info in day_schedule:
                for slot in schedule_template:
                    if slot['time'] == class_info['time']:
                        slot['subject'] = wrap_text(class_info['subject'])
                        slot['group'] = class_info['group']
                        slot['room'] = class_info['room']
                        break
            return schedule_template
    return None


def get_group_schedule(group_name, week, day):
    schedule_template = [
        {"time": "8:30", "subject": "", "room": "", "teacher": ""},
        {"time": "10:10", "subject": "", "room": "", "teacher": ""},
        {"time": "12:00", "subject": "", "room": "", "teacher": ""},
        {"time": "13:40", "subject": "", "room": "", "teacher": ""},
        {"time": "15:20", "subject": "", "room": "", "teacher": ""},
        {"time": "17:00", "subject": "", "room": "", "teacher": ""},
        {"time": "18:40", "subject": "", "room": "", "teacher": ""}
    ]
    for group in utils.group_json['groups']:
        if group['group'] == group_name:
            weeks_data = group.get('weeks', {})
            day_schedule = weeks_data.get(week, {}).get(day, None)
            if day_schedule is None:
                return None

            for class_info in day_schedule:
                for slot in schedule_template:
                    if slot['time'] == class_info['time']:
                        slot['subject'] = wrap_text(class_info['subject'])
                        slot['room'] = class_info['room']
                        slot['teacher'] = class_info['teacher']
                        break

            return schedule_template
    return None


def get_room_schedule(room_name, week, day):
    schedule_template = [
        {"time": "8:30", "subject": "", "teacher": "", "group": ""},
        {"time": "10:10", "subject": "", "teacher": "", "group": ""},
        {"time": "12:00", "subject": "", "teacher": "", "group": ""},
        {"time": "13:40", "subject": "", "teacher": "", "group": ""},
        {"time": "15:20", "subject": "", "teacher": "", "group": ""},
        {"time": "17:00", "subject": "", "teacher": "", "group": ""},
        {"time": "18:40", "subject": "", "teacher": "", "group": ""}
    ]

    for room in utils.room_json['rooms']:
        if room['room'] == room_name:
            weeks_data = room.get('weeks', {})
            day_schedule = weeks_data.get(week, {}).get(day, None)
            if day_schedule is None:
                return None

            for class_info in day_schedule:
                for slot in schedule_template:
                    if slot['time'] == class_info['time']:
                        slot['subject'] = wrap_text(class_info['subject'])
                        slot['teacher'] = class_info['teacher']
                        slot['group'] = class_info['group']
                        break

            return schedule_template
    return None
