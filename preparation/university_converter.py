# TKS VOLSU SCHEDULE BOT
# Copyright (C) 2024 N0rmalUser
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import re

from docx import Document
from progress.bar import Bar

from bot import config
from bot.database.db_init import schedule_db_init
from bot.database.schedule import Schedule


def set_default():
    for i in sorted(config.GROUPS):
        schedule_db.add_group(i)
    for i in sorted(config.ALL_PERSONAL):
        schedule_db.add_teacher(i)
    for i in sorted(config.ROOMS):
        schedule_db.add_room(i)


schedule_db_init()
schedule_db = Schedule()
set_default()
files = [f for f in os.listdir("preparation\\schedules\\") if f.endswith(".docx")]
bar = Bar("Импорт расписания университета в базу данных", max=len(files))

for file in files:
    file_path = os.path.join("preparation\\schedules\\", file)
    doc = Document(file_path)
    table = doc.tables[0]
    temp_schedule = {}
    group = file.replace(".docx", "")
    subgroup = False
    for row in table.rows[1:]:
        day, time, info = row.cells[:3]
        # if len(row.cells) == 3:
        #     day, time, info = row.cells[:3]
        # else:
        #     subgroup = True
        #     day, time, info, subinfo = row.cells[:4]
        #     print(subinfo.text)
        # TODO: Разделение по подгруппам

        parts = re.split(r"(?<=\))\s*,", re.sub(r"\s*-*\s*поток\s\d+\s*", "", info.text))
        subject = parts[0].strip()
        if subject != "":
            if len(parts) > 1 and parts[1].strip():
                auditorium_match = re.search(r"Ауд\.*.*", parts[1])
                if auditorium_match:
                    classroom = re.sub(
                        r"Спортивныйзал",
                        "Спортзал ",
                        re.sub(r"\s*", "", re.sub(r"Ауд\.*", "", auditorium_match.group())),
                    )
                    if classroom[-1] in ",;:":
                        classroom = classroom[:-1]
                    teachers_text = re.sub(
                        r"(\s*доцент\s*|\s*преподаватель\s*|\s*старший преподаватель\s*|\s*ассистент|\s*профессор\s*)",
                        "",
                        parts[1].replace(classroom, ""),
                    )
                else:
                    classroom = ""
                    teachers_text = ""

                teachers = [
                    teacher.strip() for teacher in teachers_text.split(",") if teacher.strip()
                ]
                teacher = ", ".join(teachers)
            else:
                teacher = ""
                classroom = ""
        else:
            teacher = "None"
            subject = "None"
            classroom = "None"
        formatted_time = time.text.split("-")[0]
        time = re.sub(r"\b8:30\b", "08:30", re.sub(r"\s*", "", formatted_time))
        day = re.sub(r"\s+", "", day.text)
        key = (str(day), str(time))
        if subject.strip() and teacher.strip() and classroom.strip():
            schedule_entry = {
                "Предмет": subject,
                "Преподаватель": teacher,
                "Аудитория": classroom,
            }
            if key not in temp_schedule:
                temp_schedule[key] = {
                    "Числитель": schedule_entry,
                    "Знаменатель": schedule_entry,
                }
            else:
                temp_schedule[key]["Знаменатель"] = schedule_entry
    full_schedule = {"Числитель": {}, "Знаменатель": {}}
    for (day, time), parts in temp_schedule.items():
        for part in ["Числитель", "Знаменатель"]:
            if part in parts:
                if day not in full_schedule[part]:
                    full_schedule[part][day] = {}
                full_schedule[part][day][time] = parts[part]
    group_name = os.path.splitext(file)[0]

    times = ["08:30", "10:10", "12:00", "13:40", "15:20", "17:00", "18:40"]
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

    for week_name, week_schedule in full_schedule.items():
        for day_name, day_schedule in week_schedule.items():
            for subject_time in times:
                if subject_time in day_schedule:
                    if day_schedule[subject_time]["Предмет"] == "None":
                        del full_schedule[week_name][day_name][subject_time]
        for DAY in days:
            if DAY in week_schedule:
                if full_schedule[week_name][DAY] == {}:
                    del full_schedule[week_name][DAY]

    for week_type, week_schedule in full_schedule.items():
        for day_name, day_schedule in week_schedule.items():
            for time, details in day_schedule.items():
                teacher_name = (
                    details["Преподаватель"].split(",")[0].strip()
                    if "," in details["Преподаватель"]
                    else details["Преподаватель"]
                )
                schedule_db.add_schedule(
                    time=time,
                    day_name=day_name,
                    week_type=week_type,
                    group_id=schedule_db.add_group(group_name),
                    teacher_id=schedule_db.add_teacher(teacher_name),
                    room_id=schedule_db.add_room(details["Аудитория"]),
                    subject_id=schedule_db.add_subject(details["Предмет"]),
                )
    bar.next()
bar.finish()

print("Расписания успешно сохранены в базу данных.")
