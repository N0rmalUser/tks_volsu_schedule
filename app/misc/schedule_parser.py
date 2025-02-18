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

        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            if len(cells) < 3:
                continue

            day = re.sub(r"\s+", "", cells[0])
            time = re.sub(r"\b8:30\b", "08:30", re.sub(r"\s*", "", cells[1].split("-")[0]))

            subgroups = []
            if len(cells) > 3 and cells[2] != cells[3]:
                subgroups.append((cells[2], 1))
                subgroups.append((cells[3], 2))
            else:
                subgroups.append((cells[2], 0))
            for info, subgroup in subgroups:
                parts = re.split(r"(?<=\))\s*,", re.sub(r"\s*-*\s*поток\s\d+\s*", "", info.replace("\n", "")))
                subject = parts[0]
                teachers = []
                classroom = ""
                if len(parts) > 1:
                    auditorium_match = re.search(r"Ауд\.?([^,;]*)", parts[1])
                    other = re.sub(r"Ауд\.?([^,;]*)", "", parts[1])
                    if auditorium_match:
                        classroom = re.sub(
                            r"Спортивныйзал",
                            "Спортзал",
                            re.sub(r"\s*", "", auditorium_match.group(1)))
                        teachers_list = re.sub(
                            r"\s*(?:доцент|преподаватель|старший преподаватель|ассистент|профессор)\s*",
                            "",
                            other
                        )
                        teachers = re.split(r"\s*,\s*", teachers_list)

                key = (day, time, subgroup)
                if key not in temp_schedule:
                    temp_schedule[key] = {
                        "Числитель": {
                            "subject": subject,
                            "teacher": teachers,
                            "classroom": classroom
                        },
                        "Знаменатель": {
                            "subject": subject,
                            "teacher": teachers,
                            "classroom": classroom
                        }
                    }
                else:
                    temp_schedule[key]["Знаменатель"] = {
                        "subject": subject,
                        "teacher": teachers,
                        "classroom": classroom
                    }

        group_name = os.path.splitext(file)[0]
        for (day, time, subgroup), data in temp_schedule.items():
            for week_type in ["Числитель", "Знаменатель"]:
                details = data[week_type]
                if not details["subject"] or details["subject"] == "None":
                    continue
                for teacher in details["teacher"]:
                    if len(teacher) < 1:
                        continue
                    schedule_db.add_schedule(
                        time=time,
                        day_name=day,
                        week_type=week_type,
                        group_id=schedule_db.add_group(group_name),
                        teacher_id=schedule_db.add_teacher(teacher),
                        room_id=schedule_db.add_room(details["classroom"]),
                        subject_id=schedule_db.add_subject(details["subject"]),
                        subgroup=subgroup
                    )
    logging.info("Расписания университета успешно сохранены в базу данных.")
