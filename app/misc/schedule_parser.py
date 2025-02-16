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

import logging
import os
import re

import openpyxl
import pandas as pd
from docx import Document

from app import config
from app.config import COLLEGE_SHEETS_PATH, GROUPS, GROUPS_SCHEDULE_PATH
from app.database.schedule import Schedule


def college_schedule_parser():
    days = {
        "ПН": "Понедельник",
        "ВТ": "Вторник",
        "СР": "Среда",
        "ЧТ": "Четверг",
        "ПТ": "Пятница",
        "CБ": "Суббота",  # Тут английская буква "C" вместо русской "С"
    }

    schedule_db = Schedule()
    schedule_db.clear_college()
    files = [f for f in os.listdir(COLLEGE_SHEETS_PATH) if f.endswith(".xlsx")]
    for file in files:
        file_path = os.path.join(COLLEGE_SHEETS_PATH, file)
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
            day_name = days.get(row["Unnamed: 0"])
            time = row["время"].split("-")[0]
            week_name = "Числитель" if row["время"] is not last_time else "Знаменатель"
            last_time = row["время"]
            if pd.isna(row[teacher_name]):
                continue

            split_result = re.split(r"\.\s*", row[teacher_name], maxsplit=1)
            if len(split_result) != 2:
                logging.error(f"Неверный формат группы и предмета: {row[teacher_name]}")
                continue
            parts = re.split(r'\s*преп\.\s*|\s*ауд\.\s*', split_result[1].strip())
            if len(parts) != 3:
                logging.error(f"Неверный формат данных: {split_result[1]}")
                continue
            subject = parts[0].strip().rstrip(',. ')
            room_str = parts[2].strip()
            room_name = re.sub(r'\s*ауд\.?\s*', '', room_str, flags=re.IGNORECASE).strip()
            groups = [g.strip() for g in split_result[0].split(',')]

            for group in groups:
                if group not in GROUPS:
                    schedule_db.add_schedule(
                        college=True,
                        time=re.sub(r"\b8:30\b", "08:30", re.sub(r"\s*", "", time)),
                        day_name=day_name,
                        week_type=week_name,
                        group_id=schedule_db.add_group(group),
                        teacher_id=schedule_db.add_teacher(teacher_name),
                        room_id=schedule_db.add_room(room_name),
                        subject_id=schedule_db.add_subject(subject),
                    )
    logging.info("Расписания колледжа успешно сохранены в базу данных.")


def set_default(schedule_db: Schedule):
    for i in sorted(config.GROUPS):
        schedule_db.add_group(i)
    for i in sorted(config.ALL_PERSONAL):
        schedule_db.add_teacher(i)
    for i in sorted(config.ROOMS):
        schedule_db.add_room(i)


def university_schedule_parser():
    schedule_db = Schedule()
    schedule_db.clear_university()
    set_default(schedule_db)
    files = [f for f in os.listdir(GROUPS_SCHEDULE_PATH) if f.endswith(".docx")]

    for file in files:
        file_path = os.path.join(GROUPS_SCHEDULE_PATH, file)
        doc = Document(file_path)
        table = doc.tables[0]
        temp_schedule = {}
        # group = file.replace(".docx", "")
        # subgroup = False
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
    logging.info("Расписания университета успешно сохранены в базу данных.")
