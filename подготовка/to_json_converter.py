import os
from docx import Document
import re
import json


# Функция для извлечения и форматирования расписания из одного файла
def extract_and_format_schedule(docx_file):
    doc = Document(docx_file)
    table = doc.tables[0]
    schedule = {
        "Числитель": {},
        "Знаменатель": {}
    }
    temp_schedule = {}
    position_pattern = r'(\,? доцент|\,? старший преподаватель|\,? ассистент|\,? профессор)'

    for row in table.rows[1:]:
        day, time, info = row.cells[:3]

        parts = re.split(r'(?<=\)),', info.text)
        subject = parts[0].strip()
        teacher_and_classroom = parts[1].split(",") if len(parts) > 1 else ["", ""]
        teacher = re.sub(position_pattern, '', teacher_and_classroom[0]).strip()
        classroom = teacher_and_classroom[1].strip() if len(teacher_and_classroom) > 1 else ""
        classroom = classroom.replace('Ауд. ', '').strip()
        formatted_time = time.text.split('-')[0]
        key = (day.text, formatted_time)

        # Проверяем, что есть информация о предмете, преподавателе и аудитории
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


directory_path = 'C:\\Users\\normal\\Desktop\\raspisanie\\files'
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