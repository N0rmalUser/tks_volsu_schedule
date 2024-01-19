from docx import Document
import data.config
import json
import re
import os


def clean_schedule(schedule):
    times = ['8:30', '10:10', '12:00', '13:40', '15:20', '17:00', '18:40']
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


directory_path = data.config.SCHEDULE_PATH
all_schedules = {}

for filename in os.listdir(directory_path):
    if filename.endswith('.docx'):
        file_path = os.path.join(directory_path, filename)
        doc = Document(file_path)
        table = doc.tables[0]
        temp_schedule = {}
        position_pattern = r'(\,? доцент|\,? старший преподаватель|\,? ассистент|\,? профессор)'
        auditorium_pattern = r'Ауд\..+'

        for row in table.rows[1:]:
            day, time, info = row.cells[:3]
            parts = re.split(r'(?<=\))\s*,', re.sub(r'\)\s*-\s*поток\s\d+\s*', ')', info.text))
            subject = parts[0].strip()
            if subject != '':
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
                    classroom = auditorium.replace('Ауд.', '').replace(" ", "").replace("Спортивныйзал", "Спортзал ")
                else:
                    teacher = ''
                    classroom = ''
            else:
                teacher = 'None'
                subject = 'None'
                classroom = 'None'

            formatted_time = time.text.split('-')[0]
            key = (day.text.replace(" ", ""), formatted_time.replace(" ", "").replace("08:30", "8:30"))
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

output_file_path = directory_path + 'university.json'

with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(all_schedules, output_file, ensure_ascii=False, indent=4)

print(f'Общий JSON-файл сохранен по пути: {output_file_path}')
