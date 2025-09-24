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


async def college_schedule_parser():
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
            parts = re.split(r"\s*преп\.\s*|\s*ауд\.\s*", split_result[1].strip())
            if len(parts) != 3:
                logging.error(f"Неверный формат данных: {split_result[1]}")
                continue
            subject = parts[0].strip().rstrip(",. ")
            room_str = parts[2].strip()
            room_name = re.sub(r"\s*ауд\.?\s*", "", room_str, flags=re.IGNORECASE).strip()
            groups = [g.strip() for g in split_result[0].split(",")]

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


async def university_schedule_parser():
    def _parse_info(text: str):
        """Парсит строку вида 'Предмет (Лаб), [должность] Фамилия И.О., Ауд. 1-23 К'
        -> dict(subject, teachers[list], classroom[str])"""

        if not text:
            return None
        raw = text.strip()
        # убрать ' - поток N'
        raw = re.sub(r"\s*-\s*поток\s*\d+\s*", " ", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s+", " ", raw)

        parts = re.split(r"(?<=\))\s*,\s*", raw, maxsplit=1)
        if len(parts) == 1:
            parts = re.split(r",\s*", raw, maxsplit=1)

        subject = parts[0].strip()
        rest = parts[1].strip() if len(parts) > 1 else ""

        classroom = ""
        if rest:
            aud = re.search(r"Ауд\.?\s*([^,;]+)", rest, flags=re.IGNORECASE)
            if aud:
                classroom = re.sub(r"\s*", "", aud.group(1))
                classroom = classroom.replace("Спортивныйзал", "Спортзал")
            rest = re.sub(r"Ауд\.?\s*([^,;]+)", "", rest, flags=re.IGNORECASE)

        # убрать должности
        rest = re.sub(
            r"\b(доцент|преподаватель|старший преподаватель|ассистент|профессор)\b\.?",
            "",
            rest,
            flags=re.IGNORECASE,
        )
        teachers = [t for t in (s.strip() for s in re.split(r"\s*,\s*", rest)) if t]

        return {"subject": subject, "teachers": teachers, "classroom": classroom}

    def _row_day_time(row):
        day = re.sub(r"\s+", "", row.cells[0].text.strip())
        start = row.cells[1].text.strip().split("-")[0]
        time = re.sub(r"\b8:30\b", "08:30", re.sub(r"\s*", "", start))
        return day, time

    def _process_group_cells(left: str, right: str = None, single_column: bool = False):
        """Возвращает список [(subgroup, info_dict)]."""

        left = left.strip() if left else ""
        right = right.strip() if right else ""

        if not left and not right:
            return []

        # для файлов с одной колонкой всегда subgroup=0
        if single_column:
            info = _parse_info(left)
            return [(0, info)] if info else []

        # если обе подгруппы одинаковые — считаем общим
        if left and right and left == right:
            info = _parse_info(left)
            return [(0, info)] if info else []

        out = []
        for idx, txt in ((1, left), (2, right)):
            if not txt:
                continue
            info = _parse_info(txt)
            if not info:
                continue
            # лекция всегда общая
            if re.search(r"\((?:Л|Лекция)\)", info["subject"], flags=re.IGNORECASE) or "Лекция" in info["subject"]:
                subgroup = 0
            else:
                subgroup = idx
            out.append((subgroup, info))
        return out

    schedule_db = Schedule()
    schedule_db.clear_university()
    set_default(schedule_db)

    files = [f for f in os.listdir(GROUPS_SCHEDULE_PATH) if f.endswith(".docx")]

    for file in files:
        file_path = os.path.join(GROUPS_SCHEDULE_PATH, file)
        doc = Document(file_path)
        table = doc.tables[0]
        rows = table.rows

        # --- вытащим список групп из заголовка ---
        header = [c.text.strip() for c in rows[0].cells]
        groups = []
        col = 2
        while col < len(header):
            group_name = header[col]
            if group_name:
                if col + 1 < len(header):
                    groups.append((group_name, col, col + 1, False))  # 2 колонки
                    col += 2
                else:
                    groups.append((group_name, col, None, True))  # одна колонка
                    col += 1
            else:
                col += 1

        # если в заголовке нет групп — значит, файл с одной группой
        if not groups:
            group_name = os.path.splitext(file)[0]
            if len(rows[0].cells) == 3:  # без подгрупп
                groups = [(group_name, 2, None, True)]
            elif len(rows[0].cells) >= 4:  # с подгруппами
                groups = [(group_name, 2, 3, False)]

        i = 1
        n = len(rows)
        while i < n:
            row = rows[i]
            day, time = _row_day_time(row)

            # числитель/знаменатель
            pair = None
            if i + 1 < n:
                day2, time2 = _row_day_time(rows[i + 1])
                if day2 == day and time2 == time:
                    pair = rows[i + 1]

            for group_name, col1, col2, single_column in groups:
                if col1 >= len(row.cells):
                    continue

                if pair is not None:
                    # Числитель
                    right_text = row.cells[col2].text if col2 and col2 < len(row.cells) else ""
                    for subgroup, info in _process_group_cells(row.cells[col1].text, right_text, single_column):
                        if not info or not info["subject"]:
                            continue
                        for teacher in info["teachers"] or [""]:
                            if not teacher:
                                continue
                            schedule_db.add_schedule(
                                time=time,
                                day_name=day,
                                week_type="Числитель",
                                group_id=schedule_db.add_group(group_name),
                                teacher_id=schedule_db.add_teacher(teacher),
                                room_id=schedule_db.add_room(info["classroom"]),
                                subject_id=schedule_db.add_subject(info["subject"]),
                                subgroup=subgroup,
                            )
                    # Знаменатель
                    right_text = pair.cells[col2].text if col2 and col2 < len(pair.cells) else ""
                    for subgroup, info in _process_group_cells(pair.cells[col1].text, right_text, single_column):
                        if not info or not info["subject"]:
                            continue
                        for teacher in info["teachers"] or [""]:
                            if not teacher:
                                continue
                            schedule_db.add_schedule(
                                time=time,
                                day_name=day,
                                week_type="Знаменатель",
                                group_id=schedule_db.add_group(group_name),
                                teacher_id=schedule_db.add_teacher(teacher),
                                room_id=schedule_db.add_room(info["classroom"]),
                                subject_id=schedule_db.add_subject(info["subject"]),
                                subgroup=subgroup,
                            )
                else:
                    right_text = row.cells[col2].text if col2 and col2 < len(row.cells) else ""
                    entries = _process_group_cells(row.cells[col1].text, right_text, single_column)
                    for week_type in ("Числитель", "Знаменатель"):
                        for subgroup, info in entries:
                            if not info or not info["subject"]:
                                continue
                            for teacher in info["teachers"] or [""]:
                                if not teacher:
                                    continue
                                schedule_db.add_schedule(
                                    time=time,
                                    day_name=day,
                                    week_type=week_type,
                                    group_id=schedule_db.add_group(group_name),
                                    teacher_id=schedule_db.add_teacher(teacher),
                                    room_id=schedule_db.add_room(info["classroom"]),
                                    subject_id=schedule_db.add_subject(info["subject"]),
                                    subgroup=subgroup,
                                )

            i += 2 if pair is not None else 1

    logging.info("Расписания университета успешно сохранены в базу данных.")
