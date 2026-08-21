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

import pytz
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Конфигурация приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ===== TELEGRAM =====
    tg_bot_token: str
    admin_chat_id: int = Field(
        description=(
            "ID административного чата.\n"
            "Для каждого пользователя, нажавшего «Начать», "
            "бот создаёт отдельный топик.\n"
            "Сообщения из топика пересылаются пользователю.\n"
            "Сообщения из топика #General рассылаются всем пользователям."
        ),
    )

    # ===== VK =====
    vk_bot_token: str

    # ===== DATE & TIME =====
    logging_level: str
    event_level: str

    # ===== LOGGING =====
    timezone: str
    numerator: int
    college_cron: str

    # ===== UNIVERSITY =====
    teachers: list[str]
    groups: list[str]
    rooms: list[str]

    students: dict[str, str]
    aliases: dict[str, str]

    # Вычисляется автоматически
    all_personal: list[str] = []

    # ===== COLLEGE =====
    college_id_const: int

    api_url: str
    app_url: str

    college_teachers: list[str]
    college_groups: list[str]

    @model_validator(mode="after")
    def build_all_personal(self) -> "Config":
        """Объединённый список преподавателей и сотрудников-студентов."""
        self.all_personal = sorted(set(self.teachers) | set(self.students))
        return self


config = Config()

# ===== TIMEZONE =====
TZ = pytz.timezone(config.timezone)

# ===== PATHS =====
ROOT_PATH = Path(__file__).resolve().parent.parent

DATA_PATH = ROOT_PATH / "data"
DB_PATH = DATA_PATH / "db"

LOG_FILE = DATA_PATH / "bot.log"

ACTIVITIES_DB = DB_PATH / "activities.db"
SCHEDULE_DB = DB_PATH / "schedule.db"
USERS_DB = DB_PATH / "users.db"
VK_DB = DB_PATH / "vk.db"

SCHEDULE_PATH = DATA_PATH / "schedule"

GROUPS_SCHEDULE_PATH = SCHEDULE_PATH / "groups"
TEACHERS_SHEETS_PATH = SCHEDULE_PATH / "teachers"
ROOMS_SHEETS_PATH = SCHEDULE_PATH / "rooms"

PLOT_PATH = DATA_PATH / "plot"

# ===== LOCALE =====
locale.setlocale(
    locale.LC_TIME,
    "Russian_Russia.1251" if platform.system() == "Windows" else "ru_RU.UTF-8",
)
