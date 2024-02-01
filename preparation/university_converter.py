from docx import Document
from config import ORIGINAL_SCHEDULES_PATH
import json
import os
import re
from progress.bar import Bar


def clean_schedule(schedule):
    times = ['08:30', '10:10', '12:00', '13:40', '15:20', '17:00', '18:40']
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    for week_name, week_schedule in schedule.items():
        for day_name, day_schedule in week_schedule.items():
            for subject_time in times:
                if subject_time in day_schedule:
                    if day_schedule[subject_time]["Предмет"] == "None":
                        del schedule[week_name][day_name][subject_time]
        for DAY in days:
            if DAY in week_schedule:
                if schedule[week_name][DAY] == {}:
                    del schedule[week_name][DAY]
    return schedule


all_schedules = {}
files = [f for f in os.listdir(ORIGINAL_SCHEDULES_PATH + 'schedules\\') if f.endswith('.docx')]
bar = Bar('Processing', max=len(files))

for filename in files:
    bar.next()
    if filename.endswith('.docx'):
        file_path = os.path.join(ORIGINAL_SCHEDULES_PATH + 'schedules\\', filename)
        doc = Document(file_path)
        table = doc.tables[0]
        temp_schedule = {}

        for row in table.rows[1:]:
            day, time, info = row.cells[:3]
            parts = re.split(r'(?<=\))\s*,', re.sub(r'\s*-*\s*поток\s\d+\s*', '', info.text))
            subject = parts[0].strip()
            if subject != '':
                if len(parts) > 1 and parts[1].strip():
                    auditorium_match = re.search(r'Ауд\.*.*', parts[1])
                    if auditorium_match:
                        auditorium = auditorium_match.group()
                        teachers_text = parts[1].replace(auditorium, '')
                    else:
                        auditorium = ''
                        teachers_text = ''
                    teachers_text = re.sub(
                        r'(\s*доцент\s*|\s*преподаватель\s*|\s*старший преподаватель\s*|\s*ассистент|\s*профессор\s*)',
                        '', teachers_text)
                    teachers = [teacher.strip() for teacher in teachers_text.split(',') if teacher.strip()]
                    teacher = ', '.join(teachers)
                    classroom = re.sub(r'СпортивныйзалК', 'Спортзал К',
                                       re.sub(r'\s*', '', re.sub(r'Ауд\.', '', auditorium)))
                else:
                    teacher = ''
                    classroom = ''
            else:
                teacher = 'None'
                subject = 'None'
                classroom = 'None'

            formatted_time = time.text.split('-')[0]
            time = re.sub(r'\b8:30\b', '08:30', re.sub(r'\s*', '', formatted_time))
            day = re.sub(r'\s+', '', day.text)
            key = (str(day), str(time))
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

        full_schedule = {"Числитель": {}, "Знаменатель": {}}
        for (day, time), parts in temp_schedule.items():
            for part in ["Числитель", "Знаменатель"]:
                if part in parts:
                    if day not in full_schedule[part]:
                        full_schedule[part][day] = {}
                    full_schedule[part][day][time] = parts[part]
        schedule_name = os.path.splitext(filename)[0]
        all_schedules[schedule_name] = clean_schedule(full_schedule)

output_file_path = ORIGINAL_SCHEDULES_PATH + 'university.json'

with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(all_schedules, output_file, ensure_ascii=False, indent=4)
print(f"\nОбщий JSON-файл для преподавателей сохранен по пути: {output_file_path}")
