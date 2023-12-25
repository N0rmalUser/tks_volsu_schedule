import json
from operator import itemgetter

def normalize_room_name(room):
    """ Normalize the room name by removing spaces """
    return room.replace(" ", "")

def merge_days_with_same_name(week_data):
    """ Merge days with the same name but different representations (e.g., 'Среда' and 'Среда ') """
    merged_week_data = {}
    for day, classes in week_data.items():
        normalized_day = day.strip()  # Remove trailing spaces
        if normalized_day not in merged_week_data:
            merged_week_data[normalized_day] = classes
        else:
            merged_week_data[normalized_day].extend(classes)
    return merged_week_data

def convert_schedule_for_groups(original_data):
    converted_data = {"groups": []}
    for group, week_data in original_data.items():
        group_info = {"group": group, "weeks": {}}
        for week, days in week_data.items():
            week_number = week
            group_info["weeks"][week_number] = {}
            for day, times in days.items():
                day_classes = []
                for time, details in times.items():
                    class_info = {
                        "time": time,
                        "discipline": details.get("Предмет", ""),
                        "room": details.get("Аудитория", ""),
                        "teacher": details.get("Преподаватель", "")
                    }
                    day_classes.append(class_info)
                # Sorting classes by time
                group_info["weeks"][week_number][day] = sorted(day_classes, key=itemgetter('time'))
        converted_data["groups"].append(group_info)
    return converted_data

def convert_schedule_for_teachers_with_merged_days(original_data):
    teacher_data = {}
    for group, week_data in original_data.items():
        for week, days in week_data.items():
            merged_days = merge_days_with_same_name(days)  # Merge days with the same name
            for day, times in merged_days.items():
                for time, details in times.items():
                    teacher = details.get("Преподаватель", "")
                    if teacher:
                        if teacher not in teacher_data:
                            teacher_data[teacher] = {}
                        if week not in teacher_data[teacher]:
                            teacher_data[teacher][week] = {}
                        if day not in teacher_data[teacher][week]:
                            teacher_data[teacher][week][day] = {}
                        key = (time, details.get("Предмет", ""), normalize_room_name(details.get("Аудитория", "")))
                        if key not in teacher_data[teacher][week][day]:
                            teacher_data[teacher][week][day][key] = []
                        teacher_data[teacher][week][day][key].append(group)
    converted_teacher_data = {"teachers": []}
    for teacher, weeks in teacher_data.items():
        teacher_weeks = {}
        for week, days in weeks.items():
            teacher_days = {}
            for day, classes in days.items():
                teacher_classes = []
                for class_key, groups in classes.items():
                    class_info = {
                        "time": class_key[0],
                        "discipline": class_key[1],
                        "room": class_key[2],
                        "group": ', '.join(sorted(set(groups)))  # Remove duplicate groups and sort
                    }
                    teacher_classes.append(class_info)
                # Sorting classes by time
                teacher_days[day] = sorted(teacher_classes, key=itemgetter('time'))
            teacher_weeks[week] = teacher_days
        converted_teacher_data["teachers"].append({"teacher": teacher, "weeks": teacher_weeks})
    return converted_teacher_data

def convert_schedule_for_rooms_with_group_and_room_merging(original_data):
    room_data = {}
    for group, week_data in original_data.items():
        for week, days in week_data.items():
            for day, times in days.items():
                for time, details in times.items():
                    room = normalize_room_name(details.get("Аудитория", ""))
                    if room:
                        if room not in room_data:
                            room_data[room] = {}
                        if week not in room_data[room]:
                            room_data[room][week] = {}
                        if day not in room_data[room][week]:
                            room_data[room][week][day] = {}
                        key = (time, details.get("Предмет", ""), details.get("Преподаватель", ""))
                        if key not in room_data[room][week][day]:
                            room_data[room][week][day][key] = []
                        room_data[room][week][day][key].append(group)
    converted_room_data = {"rooms": []}
    for room, weeks in room_data.items():
        room_weeks = {}
        for week, days in weeks.items():
            room_days = {}
            for day, classes in days.items():
                room_classes = []
                for class_key, groups in classes.items():
                    class_info = {
                        "time": class_key[0],
                        "discipline": class_key[1],
                        "teacher": class_key[2],
                        "group": ', '.join(sorted(set(groups)))  # Remove duplicate groups and sort
                    }
                    room_classes.append(class_info)
                # Sorting classes by time
                room_days[day] = sorted(room_classes, key=itemgetter('time'))
            room_weeks[week] = room_days
        converted_room_data["rooms"].append({"room": room, "weeks": room_weeks})
    return converted_room_data
# File paths
input_file_path = 'C:\\Users\\normal\\Desktop\\raspisanie\\подготовка\\schedule.json'
groups_output_file_path = 'C:\\Users\\normal\\Desktop\\raspisanie\\подготовка\\groups.json'
teachers_output_file_path = 'C:\\Users\\normal\\Desktop\\raspisanie\\подготовка\\teachers.json'
rooms_output_file_path = 'C:\\Users\\normal\\Desktop\\raspisanie\\подготовка\\rooms.json'

# Load the original JSON data
with open(input_file_path, 'r', encoding='utf-8') as file:
    original_data = json.load(file)

# Convert the data for groups, teachers with merged days, and rooms
converted_data_for_groups = convert_schedule_for_groups(original_data)
converted_data_for_teachers_with_merged_days = convert_schedule_for_teachers_with_merged_days(original_data)
converted_data_for_rooms_with_group_and_room_merging = convert_schedule_for_rooms_with_group_and_room_merging(original_data)

# Save the converted data to new JSON files
with open(groups_output_file_path, 'w', encoding='utf-8') as file:
    json.dump(converted_data_for_groups, file, ensure_ascii=False, indent=4)
with open(teachers_output_file_path, 'w', encoding='utf-8') as file:
    json.dump(converted_data_for_teachers_with_merged_days, file, ensure_ascii=False, indent=4)
with open(rooms_output_file_path, 'w', encoding='utf-8') as file:
    json.dump(converted_data_for_rooms_with_group_and_room_merging, file, ensure_ascii=False, indent=4)
