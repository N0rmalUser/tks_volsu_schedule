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

import openpyxl
import pandas as pd
from progress.bar import Bar

from bot.database.schedule import Schedule

days = {
    "ПН": "Понедельник",
    "ВТ": "Вторник",
    "СР": "Среда",
    "ЧТ": "Четверг",
    "ПТ": "Пятница",
    "CБ": "Суббота",  # Тут английская буква "C" вместо русской "С"
}

schedule_db = Schedule()

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
        day_name = days.get(row["Unnamed: 0"])
        time = row["время"].split("-")[0]
        week_name = "Числитель" if row["время"] is not last_time else "Знаменатель"
        last_time = row["время"]
        if pd.isna(row[teacher_name]):
            continue
        substitution = re.split(r"\.", row[teacher_name])
        groups = substitution[0]
        subject_name = re.sub(r"\s*,*\s*преп.*$", "", re.sub(r"^\s*", "", substitution[1])) + ")"
        room_name = (
            re.sub(r"(\s*|,*|ауд)", "", substitution[-1])
            if substitution[-1] != ""
            else re.sub(r"(\s*|,*|ауд)", "", substitution[-2])
        )
        group_name = list(set([i.strip() for i in groups.split(",")]))
        print(group_name)
        for i in range(len(group_name)):
            print(group_name[i], week_name)
            schedule_db.add_schedule(
                college=True,
                time=re.sub(r"\b8:30\b", "08:30", re.sub(r"\s*", "", time)),
                day_name=day_name,
                week_type=week_name,
                group_id=schedule_db.add_group(group_name[i]),
                teacher_id=schedule_db.add_teacher(teacher_name),
                room_id=schedule_db.add_room(room_name),
                subject_id=schedule_db.add_subject(subject_name),
            )
bar.finish()
print("Расписания успешно сохранены в базу данных.")
