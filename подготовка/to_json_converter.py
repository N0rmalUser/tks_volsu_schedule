import os
from docx import Document
import re
import json


def extract_and_format_schedule(docx_file):
    doc = Document(docx_file)
    table = doc.tables[0]
    schedule = {"Числитель": {},"Знаменатель": {}}
    temp_schedule = {}
    position_pattern = r'(\,? доцент|\,? старший преподаватель|\,? ассистент|\,? профессор)'
    auditorium_pattern = r'Ауд\..+'

    for row in table.rows[1:]:
        day, time, info = row.cells[:3]

        parts = re.split(r'(?<=\)),', info.text)
        subject = parts[0].strip()

        if len(parts) > 1 and parts[1].strip():
            auditorium_match = re.search(auditorium_pattern, parts[1])
            if auditorium_match:
                auditorium = auditorium_match.group()
                teachers_text = parts[1].replace(auditorium, '')
            else:
                auditorium = ''
                teachers_text = ''
            teachers_text = re.sub(position_pattern, '', teachers_text)
            teachers = [teacher.strip() for teacher in teachers_text.split(',') if teacher.strip()]
            teacher = ', '.join(teachers)
            classroom = auditorium.replace('Ауд.', '').replace(" ", "").replace("Спортивныйзал", "")
        else:
            teacher = ''
            classroom = ''

        formatted_time = time.text.split('-')[0]
        key = (day.text, formatted_time)

        if subject.strip() and teacher.strip() and classroom.strip():
            schedule_entry = {
                "Предмет": subject,
                "Преподаватель": teacher,
                "Аудитория": classroom
            }

            if key not in temp_schedule:
                temp_schedule[key] = {"Числитель": schedule_entry, "Знаменатель": schedule_entry}
            else:
                temp_schedule[key]["Знаменатель"] = schedule_entry

    for (day, time), parts in temp_schedule.items():
        for part in ["Числитель", "Знаменатель"]:
            if part in parts:
                if day not in schedule[part]:
                    schedule[part][day] = {}
                schedule[part][day][time] = parts[part]

    return schedule


directory_path = 'C:\\Users\\normal\\Desktop\\raspisanie\\подготовка\\расписания'
all_schedules = {}

for filename in os.listdir(directory_path):
    if filename.endswith('.docx'):
        file_path = os.path.join(directory_path, filename)
        schedule = extract_and_format_schedule(file_path)
        schedule_name = os.path.splitext(filename)[0]
        all_schedules[schedule_name] = schedule

output_file_path = 'C:\\Users\\normal\\Desktop\\raspisanie\\schedule.json'

with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(all_schedules, output_file, ensure_ascii=False, indent=4)

print(f'Общий JSON-файл сохранен по пути: {output_file_path}')
