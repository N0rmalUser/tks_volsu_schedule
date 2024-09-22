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

import toml
from progress.bar import Bar
from requests import post

config = toml.load(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.toml")))
teachers: dict[str, str] = config["college"]["teachers"]
admin_id: int = config["bot"]["admin_id"]
bar = Bar("Импорт расписания колледжа", max=len(list(teachers.keys())))
for teacher in teachers.values():
    bar.next()
    post(
        url="https://app.volsu.ru/api/bot/select-teacher",
        json={"teacherId": teacher, "telegramId": admin_id, "start": "download"},
    )
bar.finish()
print("Расписание успешно отправлено в бота телеги")
