import os
import re
import sqlite3

import openpyxl
import pandas as pd
from progress.bar import Bar

DATABASE_PATH = "schedule.db"


def convert_day_name(day_short):
    days = {
        "ПН": "Понедельник",
        "ВТ": "Вторник",
        "СР": "Среда",
        "ЧТ": "Четверг",
        "ПТ": "Пятница",
        "СБ": "Суббота",
    }
    return days.get(day_short, day_short)


def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS CollegeSchedule (
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
                FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID))"""
    )
    conn.commit()
    conn.close()


def insert_into_database(tm, day, week, room, subject, group, teacher):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT GroupID FROM Groups WHERE GroupName = ?", (group,))
    group_id = cursor.fetchone()
    if group_id is None:
        cursor.execute("INSERT INTO Groups (GroupName) VALUES (?)", (group,))
        conn.commit()
        group_id = cursor.lastrowid
    else:
        group_id = group_id[0]

    # Используем обработанное имя преподавателя
    cursor.execute("SELECT TeacherID FROM Teachers WHERE TeacherName = ?", (teacher,))
    teacher_id = cursor.fetchone()
    if teacher_id is None:
        cursor.execute("INSERT INTO Teachers (TeacherName) VALUES (?)", (teacher,))
        conn.commit()
        teacher_id = cursor.lastrowid
    else:
        teacher_id = teacher_id[0]

    cursor.execute("SELECT RoomID FROM Rooms WHERE RoomNumber = ?", (room,))
    room_id = cursor.fetchone()
    if room_id is None:
        cursor.execute("INSERT INTO Rooms (RoomNumber) VALUES (?)", (room,))
        conn.commit()
        room_id = cursor.lastrowid
    else:
        room_id = room_id[0]

    cursor.execute("SELECT SubjectID FROM Subjects WHERE SubjectName = ?", (subject,))
    subject_id = cursor.fetchone()
    if subject_id is None:
        cursor.execute("INSERT INTO Subjects (SubjectName) VALUES (?)", (subject,))
        conn.commit()
        subject_id = cursor.lastrowid
    else:
        subject_id = subject_id[0]

    cursor.execute(
        "INSERT INTO CollegeSchedule (Time, DayOfWeek, WeekType, GroupID, TeacherID, RoomID, SubjectID) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tm, day, week, group_id, teacher_id, room_id, subject_id),
    )
    conn.commit()
    conn.close()


def main():
    initialize_database()
    files = [f for f in os.listdir("preparation\\schedules\\") if f.endswith(".xlsx")]
    bar = Bar("Импорт расписания колледжа в базу данных", max=len(files))

    for file in files:
        bar.next()
        file_path = os.path.join("preparation\\schedules\\", file)
        teacher_name = re.sub(
            r"_",
            r".",
            re.sub(
                r"([А-ЯЁа-яёA-Za-z]{2,})_",
                r"\1 ",
                re.findall(r"расписание_занятий_(\w+_\w[.|_]\w\.)", file)[0],
            ),
        )
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

        last_time = "None"
        for index, row in df.iterrows():
            day_name = convert_day_name(row["Unnamed: 0"])
            time = row["время"].split("-")[0]
            week_name = "Числитель" if row["время"] is not last_time else "Знаменатель"
            last_time = row["время"]
            if pd.isna(row[teacher_name]):
                continue
            substitution = re.split(r"\.", row[teacher_name])
            groups = substitution[0]
            subject_name = (
                re.sub(r"\s*,*\s*преп.*$", "", re.sub(r"^\s*", "", substitution[1]))
                + ")"
            )
            room_name = (
                re.sub(r"(\s*|,*|ауд)", "", substitution[-1])
                if substitution[-1] != ""
                else re.sub(r"(\s*|,*|ауд)", "", substitution[-2])
            )
            group_name = list(set([i.strip() for i in groups.split(",")]))
            if len(group_name) > 1:
                for group in group_name:
                    insert_into_database(
                        time,
                        day_name,
                        week_name,
                        room_name,
                        subject_name,
                        group,
                        teacher_name,
                    )
            insert_into_database(
                time,
                day_name,
                week_name,
                room_name,
                subject_name,
                group_name[0],
                teacher_name,
            )
    bar.finish()
    print("Расписания успешно сохранены в базу данных.")


if __name__ == "__main__":
    main()
