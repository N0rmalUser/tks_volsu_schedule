import sqlite3
import re


def get_or_insert_group(group_name):
    cursor.execute('SELECT GroupID FROM Groups WHERE GroupName = ?', (group_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute('INSERT INTO Groups (GroupName) VALUES (?)', (group_name,))
        return cursor.lastrowid


def get_or_insert_teacher(teacher_name):
    cursor.execute('SELECT TeacherID FROM Teachers WHERE TeacherName = ?', (teacher_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute('INSERT INTO Teachers (TeacherName) VALUES (?)', (teacher_name,))
        return cursor.lastrowid


def get_or_insert_subject(subject_name):
    cursor.execute('SELECT SubjectID FROM Subjects WHERE SubjectName = ?', (subject_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute('INSERT INTO Subjects (SubjectName) VALUES (?)', (subject_name,))
        return cursor.lastrowid


def get_or_insert_room(room_name):
    cursor.execute('SELECT RoomID FROM Rooms WHERE RoomNumber = ?', (room_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute('INSERT INTO Rooms (RoomNumber) VALUES (?)', (room_name,))
        return cursor.lastrowid


def main(day_n, week_n, para, lesson, group):
    times = ['08:30', '10:10', '12:00', '13:40', '15:20', '17:00', '18:40']
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    day = days[day_n - 1]
    time = times[para - 1]
    week = 'Числитель' if week_n == 1 else 'Знаменатель'

    teacher = re.search(r'преп.\s*(\w*\s*[А-Я]*\.\s*[А-Я]*\.)', lesson).group(1)
    substitution = re.split(r'\.', lesson)
    subject = re.search(r'(.*)преп', lesson).group(1)
    room = re.sub(r'(\s*|,*|ауд)', '', substitution[-1]) if substitution[-1] != '' else re.sub(r'(\s*|,*|ауд)', '', substitution[-2])

    print(time, day, week)
    print(f'{teacher}\n{room}\n{subject}')

    group_id = get_or_insert_group(group)
    teacher_id = get_or_insert_teacher(teacher)
    subject_id = get_or_insert_subject(subject)
    room_id = get_or_insert_room(room)

    cursor.execute('''INSERT INTO schedule (Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (time, day, week, group_id, teacher_id, room_id, subject_id))


connection = sqlite3.connect('schedule.db')
cursor = connection.cursor()

day_n = 6
week_n = 1
para = 4
lesson = 'Технология выполнения работ по рабочей профессии Монтажник оборудования связи (л.) преп. Семенова О.В. Ауд. 2-06М'
group = 'ИССк-191'

main(day_n, week_n, para, lesson, group)


connection.commit()
connection.close()
