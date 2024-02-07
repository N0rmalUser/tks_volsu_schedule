import json
from typing import Any
from config import ORIGINAL_SCHEDULES_PATH


def transform_schedule(input_schedule: dict) -> dict[str, list[Any] | dict[Any, Any] | list[dict[str, Any]]]:
    transformed = {
        "groups": [],
        "teachers": {}
    }

    for group, weeks in input_schedule.items():
        group_schedule = {
            "group": group,
            "weeks": {}
        }
        for week_type, days in weeks.items():
            week_schedule = {}
            for day, times in days.items():
                day_schedule = []
                for time, details in times.items():
                    class_info = {
                        "time": time,
                        "subject": details["Предмет"],
                        "room": details["Аудитория"],
                        "teacher": details["Преподаватель"]
                    }

                    day_schedule.append(class_info)
                    teacher_name = details["Преподаватель"]
                    if teacher_name not in transformed["teachers"]:
                        transformed["teachers"][teacher_name] = {"weeks": {}}
                    if week_type not in transformed["teachers"][teacher_name]["weeks"]:
                        transformed["teachers"][teacher_name]["weeks"][week_type] = {}
                    if day not in transformed["teachers"][teacher_name]["weeks"][week_type]:
                        transformed["teachers"][teacher_name]["weeks"][week_type][day] = []
                    teacher_class_info = {
                        "time": class_info["time"],
                        "subject": class_info["subject"],
                        "room": class_info["room"],
                        "group": group
                    }
                    transformed["teachers"][teacher_name]["weeks"][week_type][day].append(teacher_class_info)
                week_schedule[day] = day_schedule
            group_schedule["weeks"][week_type] = week_schedule
        transformed["groups"].append(group_schedule)
    teachers_list = [{"teacher": key, "weeks": value["weeks"]} for key, value in transformed["teachers"].items()]
    transformed["teachers"] = teachers_list

    return transformed


def merge_schedules(university_schedule: dict, college_schedule: dict) -> list[dict[str, Any]]:
    existing_schedule_dict = {teacher['teacher']: teacher['weeks'] for teacher in university_schedule}

    for teacher in college_schedule['teachers']:
        teacher_name = teacher['teacher']
        if teacher_name not in existing_schedule_dict:
            existing_schedule_dict[teacher_name] = teacher['weeks']
        else:
            for week_type, days in teacher['weeks'].items():
                if week_type not in existing_schedule_dict[teacher_name]:
                    existing_schedule_dict[teacher_name][week_type] = days
                else:
                    for day, classes in days.items():
                        if day not in existing_schedule_dict[teacher_name][week_type]:
                            existing_schedule_dict[teacher_name][week_type][day] = classes
                        else:
                            existing_classes = [class_detail['time'] for class_detail in
                                                existing_schedule_dict[teacher_name][week_type][day]]
                            for class_detail in classes:
                                class_detail_without_teacher = {key: value for key, value in class_detail.items() if
                                                                key != 'teacher'}
                                if class_detail['time'] not in existing_classes:
                                    existing_schedule_dict[teacher_name][week_type][day].append(
                                        class_detail_without_teacher)
    updated_schedule = [{"teacher": key, "weeks": value} for key, value in existing_schedule_dict.items()]
    return updated_schedule


def transform_to_room_schedule(input_schedule: dict) -> list[dict[str, Any]]:
    room_schedule = {}
    for teacher_schedule in input_schedule['teachers']:
        for week_type, days in teacher_schedule['weeks'].items():
            for day, classes in days.items():
                for class_info in classes:
                    room = class_info['room']
                    if room not in room_schedule:
                        room_schedule[room] = {"Числитель": {}, "Знаменатель": {}}
                    if day not in room_schedule[room][week_type]:
                        room_schedule[room][week_type][day] = []

                    room_class_info = {
                        "time": class_info["time"],
                        "subject": class_info["subject"],
                        "teacher": teacher_schedule["teacher"],
                        "group": class_info["group"]
                    }
                    room_schedule[room][week_type][day].append(room_class_info)
    room_schedule_list = [{"room": key, "weeks": value} for key, value in room_schedule.items()]
    return room_schedule_list


directory_path = ORIGINAL_SCHEDULES_PATH

with open(directory_path + 'university.json', 'r', encoding='utf-8') as file:
    input_data = json.load(file)

transformed_schedule = transform_schedule(input_data)

with open(directory_path + 'college.json', 'r', encoding='utf-8') as file:
    additional_data = json.load(file)

transformed_schedule['teachers'] = merge_schedules(transformed_schedule['teachers'], additional_data)

with open(directory_path + 'combined_schedule.json', 'w', encoding='utf-8') as file:
    json.dump(transformed_schedule, file, ensure_ascii=False, indent=4)
    print(f"Общий JSON-файл для преподавателей сохранен по пути: {directory_path}combined_schedule.json")
