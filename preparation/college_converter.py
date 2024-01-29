import json
import os

import openpyxl
import pandas as pd

import data.config

import re

from progress.bar import Bar


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
    substitution = re.split(r'\.', subject_info)
    return (
        re.sub(r'\s*,*\s*преп.*$', '', re.sub(r'^\s*', '', substitution[1])),
        re.sub(r'(\s*|,*|ауд)', '', substitution[-1]) if substitution[-1] != '' else re.sub(r'(\s*|,*|ауд)', '', substitution[-2]),
        substitution[0]
    )


directory_path = data.config.ORIGINAL_SCHEDULES_PATH + 'schedules\\'
files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx')]
teachers_schedule = {"teachers": []}
rooms_schedule = {"rooms": []}
bar = Bar('Формирование расписания для колледжа', max=len(files))

for file in files:
    bar.next()
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
    teacher_name = re.search(r'_(.*)xlsx', file).group(1)
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

        if pd.isna(row[teacher_name]):
            continue
        substitution = re.split(r'\.', row[teacher_name])
        group = substitution[0]
        subject = re.sub(r'\s*,*\s*преп.*$', '', re.sub(r'^\s*', '', substitution[1]))
        room = re.sub(r'(\s*|,*|ауд)', '', substitution[-1]) if substitution[-1] != '' else re.sub(r'(\s*|,*|ауд)', '', substitution[-2])
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

output_file_path = data.config.ORIGINAL_SCHEDULES_PATH + 'college.json'

with open(output_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(teachers_schedule, json_file, ensure_ascii=False, indent=4)
    print(f"\nОбщий JSON-файл для преподавателей сохранен по пути: {output_file_path}")
