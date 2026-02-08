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

import asyncio
import logging
import os
import re
from collections.abc import Coroutine
from datetime import date, datetime, timedelta

from aiohttp import ClientSession
from docx import Document
from docx.table import _Row

from app.config import (
    ALL_PERSONAL,
    API_URL,
    APP_URL,
    COLLEGE_GROUPS,
    COLLEGE_TEACHERS,
    GROUPS,
    GROUPS_SCHEDULE_PATH,
    ROOMS,
)
from app.database.schedule import Schedule

# Предполагается, что следующие глобальные константы / структуры
# определены в окружении, из которого вызывается функция:
# APP_URL, API_URL, COLLEGE_TEACHERS (set/list of teacher short names),
# COLLEGE_GROUPS (list of group prefixes), GROUPS (iterable of group names)
# Класс Schedule с методами: clear_college, add_group, add_teacher, add_room, add_subject, add_schedule


async def college_schedule_parser() -> None:
    days_map = {
        "monday": "Понедельник",
        "tuesday": "Вторник",
        "wednesday": "Среда",
        "thursday": "Четверг",
        "friday": "Пятница",
        "saturday": "Суббота",
        "sunday": "Воскресенье",
    }
    week_map = {"numerator": "Числитель", "denominator": "Знаменатель"}

    def get_week_timestamps() -> tuple[int, int]:
        now = datetime.now()
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=13, hours=23, minutes=59, seconds=59)
        return int(start.timestamp() * 1000), int(end.timestamp() * 1000)

    def get_semester(admission_year: int, now_date: date) -> int:
        start = date(admission_year, 9, 1)
        if now_date < start:
            return 0
        semester = 1 + (now_date.year - admission_year) * 2
        if now_date.year == admission_year and now_date.month < 9:
            return 0
        if now_date.month < 1:
            semester -= 2
        elif now_date.month < 9:
            semester -= 1
        return semester

    min_ts, max_ts = get_week_timestamps()
    now_date = date.today()

    async with ClientSession(headers={"provider": "volsu-system-bot"}) as session:
        try:
            teachers = await (await session.get(API_URL.format(type="teacher"))).json()
            groups = await (await session.get(API_URL.format(type="group"))).json()

            tks_teacher_map = {
                f"{t['firstName']} {t['surname'][0]}.{t['patronymic'][0]}.": t["id"]
                for t in teachers
                if f"{t['firstName']} {t['surname'][0]}.{t['patronymic'][0]}." in COLLEGE_TEACHERS
            }
            all_groups_map = {g["id"]: g["name"] for g in groups}
            tks_groups_map = {
                g["name"]: (g["id"], g["admissionYear"])
                for g in groups
                if any(g["name"].startswith(college) for college in COLLEGE_GROUPS)
            }

            schedule = Schedule()
            schedule.clear_college()
            logging.info("Очистил расписание колледжа, начинаю парсинг")

            async def fetch(url: str) -> Coroutine:
                async with session.get(url) as r:
                    return await r.json()

            tasks = []

            for teacher_name, teacher_id in tks_teacher_map.items():
                url = f"{APP_URL}/teacher/{teacher_id}?minTimestamp={min_ts}&maxTimestamp={max_ts}"
                tasks.append(("teacher", teacher_name, fetch(url)))

            for group_name, (group_id, year) in tks_groups_map.items():
                semester = get_semester(year, now_date)
                url = f"{APP_URL}/group/{group_id}?minTimestamp={min_ts}&maxTimestamp={max_ts}&semester={semester}"
                tasks.append(("group", group_name, fetch(url)))

            results = await asyncio.gather(*(t[2] for t in tasks))

            for (kind, name, _), lessons in zip(tasks, results, strict=False):
                for lesson in lessons:
                    if kind == "group" and lesson["subject"] == "":
                        continue

                    start_time = str(lesson["startTime"]).zfill(4)
                    time_str = re.sub(r"\b8:30\b", "08:30", f"{start_time[:2]}:{start_time[2:]}")
                    day_name = days_map.get(lesson["day"].lower(), lesson["day"])
                    week_type = week_map.get(lesson["week"], lesson["week"])
                    room_name = lesson["classrooms"][0] if lesson["classrooms"] else "Не указано"

                    subject = lesson["subject"].strip()
                    teacher_name = name if kind == "teacher" else "N/A"

                    match = re.search(r"преп\.?\s+([А-яЁё]+\s+[А-ЯЁ]\.[А-ЯЁ]\.)", subject, re.IGNORECASE)
                    if match:
                        teacher_name = match.group(1)

                    subject = re.sub(r",?\s*?преп.*", "", subject, flags=re.IGNORECASE)

                    group_name = name if kind == "group" else all_groups_map.get(lesson["groupId"])

                    if kind == "teacher" and group_name in GROUPS:
                        continue

                    schedule.add_schedule(
                        college=True,
                        time=time_str,
                        day_name=str(day_name),
                        week_type=str(week_type),
                        group_id=schedule.add_group(str(group_name)),
                        teacher_id=schedule.add_teacher(teacher_name),
                        room_id=schedule.add_room(room_name),
                        subject_id=schedule.add_subject(subject),
                    )

        except Exception as e:
            logging.error(e)

    logging.info("Обновлено расписание колледжа для всех преподавателей")


async def university_schedule_parser() -> None:
    def _split_lessons(text: str) -> list[str]:
        if not text:
            return []
        text = re.sub(r"^\s*\d{1,2}:\d{2}-\d{1,2}:\d{2}\s*", "", text).strip()
        if "Дисциплина по выбору:" not in text:
            return [text]
        prefix = "Дисциплина по выбору:"
        text_wo_prefix = text.split(prefix, 1)[1].strip()
        parts = [p.strip() for p in text_wo_prefix.split(";") if p.strip()]
        return [f"{prefix} {p}" for p in parts]

    def _parse_info(text: str) -> dict[str, str | list[str]]:
        """Парсит строку вида 'Предмет (Лаб), [должность] Фамилия И.О., Ауд. 1-23 К'
        -> dict(subject[str], teachers[list], classroom[str])"""

        if not text:
            return {}
        raw = text.strip()

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

        rest = re.sub(
            r"\b(доцент|преподаватель|старший преподаватель|ассистент|профессор)\b\.?",
            "",
            rest,
            flags=re.IGNORECASE,
        )
        teachers = [t for t in (s.strip() for s in re.split(r"\s*,\s*", rest)) if t]

        return {"subject": subject, "teachers": teachers, "classroom": classroom}

    def _row_day_time(row: _Row) -> tuple[str, str]:
        day = re.sub(r"\s+", "", row.cells[0].text.strip())
        start = row.cells[1].text.strip().split("-")[0]
        time = re.sub(r"\b8:30\b", "08:30", re.sub(r"\s*", "", start))
        return day, time

    def _set_default() -> None:
        for i in sorted(GROUPS):
            schedule_db.add_group(i)
        for i in sorted(ALL_PERSONAL):
            schedule_db.add_teacher(i)
        for i in sorted(ROOMS):
            schedule_db.add_room(i)

    def _parse(text: str) -> list[dict[str, str | list[str]]]:
        lessons = _split_lessons(text)
        return [_parse_info(lesson) for lesson in lessons]

    schedule_db = Schedule()
    schedule_db.clear_university()
    _set_default()

    files = [f for f in os.listdir(GROUPS_SCHEDULE_PATH) if f.endswith(".docx")]

    for file in files:
        doc = Document(os.path.join(GROUPS_SCHEDULE_PATH, file))
        table = doc.tables[0]
        rows = table.rows

        header = [c.text.strip() for c in rows[0].cells]
        groups: list[tuple[str, int, int]] = []
        col = 2
        seen = {}

        for group_name in header[2:]:
            seen[group_name] = seen.get(group_name, 0) + 1

            if header.count(group_name) == 1:
                subgroup = 0
            else:
                subgroup = seen[group_name]

            groups.append((group_name, col, subgroup))
            col += 1

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

            for group_name, column, subgroup in groups:
                if pair:
                    week_sources = [
                        ("Числитель", rows[i].cells[column].text),
                        ("Знаменатель", rows[i + 1].cells[column].text),
                    ]
                else:
                    text = row.cells[column].text
                    week_sources = [("Числитель", text), ("Знаменатель", text)]

                for week_type, text in week_sources:
                    if not text:
                        continue

                    for info in _parse(text):
                        for teacher in info["teachers"]:
                            schedule_db.add_schedule(
                                time=time,
                                day_name=day,
                                week_type=week_type,
                                group_id=schedule_db.add_group(group_name),
                                teacher_id=schedule_db.add_teacher(teacher),
                                room_id=schedule_db.add_room(str(info["classroom"])),
                                subject_id=schedule_db.add_subject(str(info["subject"])),
                                subgroup=subgroup,
                            )

            i += 2 if pair is not None else 1

    logging.info("Расписания университета успешно сохранены в базу данных.")
