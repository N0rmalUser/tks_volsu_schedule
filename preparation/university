from docx import Document
from config import ORIGINAL_SCHEDULES_PATH
import sqlite3
import os
import re
from progress.bar import Bar

DATABASE_PATH = 'schedule.db'


def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Groups (
                        GroupID INTEGER PRIMARY KEY AUTOINCREMENT,
                        GroupName TEXT UNIQUE NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Teachers (
                        TeacherID INTEGER PRIMARY KEY AUTOINCREMENT,
                        TeacherName TEXT UNIQUE NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Rooms (
                        RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
                        RoomNumber TEXT UNIQUE NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Subjects (
                        SubjectID INTEGER PRIMARY KEY AUTOINCREMENT,
                        SubjectName TEXT UNIQUE NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Schedule (
                        ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Time TEXT NOT NULL,
                        DayOfWeek TEXT NOT NULL,
                        WeekType TEXT NOT NULL,
                        GroupID INTEGER,
                        TeacherID INTEGER,
                        RoomID INTEGER,
                        SubjectID INTEGER,
                        FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
                        FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
                        FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
                        FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID))''')

    conn.commit()
    conn.close()


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


def insert_into_database(schedule_name, schedule):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    for week_type, week_schedule in schedule.items():
        for day_name, day_schedule in week_schedule.items():
            for time, details in day_schedule.items():
                # Обработка строки преподавателя для извлечения только имени
                teacher_name = details["Преподаватель"].split(',')[0].strip() if "," in details["Преподаватель"] else \
                details["Преподаватель"]

                cursor.execute("SELECT GroupID FROM Groups WHERE GroupName = ?", (schedule_name,))
                group_id = cursor.fetchone()
                if group_id is None:
                    cursor.execute("INSERT INTO Groups (GroupName) VALUES (?)", (schedule_name,))
                    conn.commit()
                    group_id = cursor.lastrowid
                else:
                    group_id = group_id[0]

                # Используем обработанное имя преподавателя
                cursor.execute("SELECT TeacherID FROM Teachers WHERE TeacherName = ?", (teacher_name,))
                teacher_id = cursor.fetchone()
                if teacher_id is None:
                    cursor.execute("INSERT INTO Teachers (TeacherName) VALUES (?)", (teacher_name,))
                    conn.commit()
                    teacher_id = cursor.lastrowid
                else:
                    teacher_id = teacher_id[0]

                cursor.execute("SELECT RoomID FROM Rooms WHERE RoomNumber = ?", (details["Аудитория"],))
                room_id = cursor.fetchone()
                if room_id is None:
                    cursor.execute("INSERT INTO Rooms (RoomNumber) VALUES (?)", (details["Аудитория"],))
                    conn.commit()
                    room_id = cursor.lastrowid
                else:
                    room_id = room_id[0]

                cursor.execute("SELECT SubjectID FROM Subjects WHERE SubjectName = ?", (details["Предмет"],))
                subject_id = cursor.fetchone()
                if subject_id is None:
                    cursor.execute("INSERT INTO Subjects (SubjectName) VALUES (?)", (details["Предмет"],))
                    conn.commit()
                    subject_id = cursor.lastrowid
                else:
                    subject_id = subject_id[0]

                cursor.execute(
                    "INSERT INTO Schedule (Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (time, day_name, week_type, group_id, teacher_id, room_id, subject_id))
    conn.commit()
    conn.close()


initialize_database()
all_schedules = {}
files = [f for f in os.listdir(ORIGINAL_SCHEDULES_PATH + 'schedules\\') if f.endswith('.docx')]
bar = Bar('Processing', max=len(files))

for filename in files:
    bar.next()
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
                    r'(\s*доцент\s*|\s*преподаватель\s*|\s*старший преподаватель\s*|\s*ассистент|\s*профессор\s*)', '',
                    teachers_text)
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
            schedule_entry = {"Предмет": subject, "Преподаватель": teacher, "Аудитория": classroom}
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
    insert_into_database(schedule_name, clean_schedule(full_schedule))
bar.finish()

print("Расписания успешно сохранены в базу данных.")
