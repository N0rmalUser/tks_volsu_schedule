import json
import os

import openpyxl
import pandas as pd

import data.config


def convert_day_name(day_short):
    days = {
        "ПН": "Понедельник",
        "ВТ": "Вторник",
        "СР": "Среда",
        "ЧТ": "Четверг",
        "ПТ": "Пятница",
        "СБ": "Суббота"
    }
    return days.get(day_short, day_short)


def split_subject_info(subject_info):
    if pd.isna(subject_info):
        return None, None, None

    return (subject_info.split('. ')[1].replace('преп', '').replace(', ', ''),
            subject_info.split(' ')[-1].replace('ауд.', '').replace('Ауд.', '').replace('.', ''),
            subject_info.split('.')[0])


directory_path = data.config.ORIGINAL_SCHEDULES_PATH
files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx')]
teachers_schedule = {"teachers": []}
rooms_schedule = {"rooms": []}

for file in files:
    file_path = os.path.join(directory_path, file)
    df = pd.read_excel(file_path)
    excel = openpyxl.load_workbook(filename=file_path)
    sheet = excel.worksheets[0]

    for r in sheet.merged_cells.ranges:
        cl, rl, cr, rr = r.bounds
        rl -= 2
        rr -= 1
        cl -= 1
        base_value = df.iloc[rl, cl]
        df.iloc[rl:rr, cl:cr] = base_value

    teacher_name = file.replace('teacher_', '').replace('xlsx', '')
    teacher_schedule = {
        "teacher": teacher_name,
        "weeks": {"Числитель": {}, "Знаменатель": {}}
    }

    last_time = 'None'
    for index, row in df.iterrows():
        day = convert_day_name(row['Unnamed: 0'])
        time = row['время'].split('-')[0]
        qq = row['время']
        isNumerator = True if row['время'] != last_time else False
        last_time = row['время']
        subject, room, group = split_subject_info(row[teacher_name])
        if subject is None:
            continue
        if isNumerator:
            if day not in teacher_schedule['weeks']['Числитель']:
                teacher_schedule['weeks']['Числитель'][day] = []
            teacher_schedule['weeks']['Числитель'][day].append({
                "time": time,
                "subject": subject,
                "room": room,
                "group": group
            })
        else:
            if day not in teacher_schedule['weeks']['Знаменатель']:
                teacher_schedule['weeks']['Знаменатель'][day] = []
            teacher_schedule['weeks']['Знаменатель'][day].append({
                "time": time,
                "subject": subject,
                "room": room,
                "group": group
            })

    teachers_schedule['teachers'].append(teacher_schedule)
    rooms_schedule['rooms'].append(teacher_schedule)

with open(directory_path+'college.json', 'w', encoding='utf-8') as json_file:
    json.dump(teachers_schedule, json_file, ensure_ascii=False, indent=4)
    print(f"Общий JSON-файл для преподавателей сохранен по пути: {directory_path + 'college.json'}")
