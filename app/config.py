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

import locale
import platform
from pathlib import Path

import toml

root_path = Path(__file__).parent.parent.resolve()

config = toml.load(root_path / "config.toml")

NUMERATOR: int = config["date"]["numerator"]

BOT_TOKEN: str = config["bot"]["token"]
ADMIN_CHAT_ID: int = config["bot"]["admin_chat_id"]
ADMIN_ID: int = config["bot"]["admin_id"]

LOG_FILE: str = config["logging"]["logfile"]

LOG_LEVEL = config["logging"]["level"]
EVENT_LEVEL = config["logging"]["event_level"]

GROUPS: list[str] = config["university"]["groups"]
TEACHERS: list[str] = config["university"]["teachers"]
ROOMS: list = config["university"]["rooms"]

STUDENTS = config["university"]["students"]
ALL_PERSONAL = sorted(set(TEACHERS) | set(STUDENTS.keys()))

COLLEGE_CONST: int = config["college"]["id_const"]
COLLEGE_TEACHERS: dict[str, str] = config["college"]["teachers"]
COLLEGE_TEACHERS_ID: list = list(config["college"]["teachers"].values())

TIMEZONE: str = config["date"]["timezone"]

DATA_PATH: Path = root_path / "data"
ACTIVITIES_DB: Path = DATA_PATH / "db" / "activities.db"
SCHEDULE_DB: Path = DATA_PATH / "db" / "schedule.db"
USERS_DB: Path = DATA_PATH / "db" / "users.db"

SCHEDULE_PATH: Path = DATA_PATH / "schedule"
SCHEDULE_TEMPLATE_PATH: Path = SCHEDULE_PATH / "template.xlsx"
GROUPS_SCHEDULE_PATH: Path = SCHEDULE_PATH / "groups"
TEACHERS_SHEETS_PATH: Path = SCHEDULE_PATH / "teachers"
ROOMS_SHEETS_PATH: Path = SCHEDULE_PATH / "rooms"
COLLEGE_SHEETS_PATH: Path = SCHEDULE_PATH / "college"
ZIP_FILE_PATH: Path = SCHEDULE_PATH / "schedules.zip"

PLOT_PATH: Path = DATA_PATH / "plot"

locale.setlocale(
    locale.LC_TIME, "Russian_Russia.1251" if platform.system() == "Windows" else "ru_RU.UTF-8"
)
