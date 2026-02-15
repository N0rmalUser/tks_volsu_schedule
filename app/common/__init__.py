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

from datetime import datetime, date

from app.config import NUMERATOR, TZ
from app.common.states import BroadcastStates


def get_today() -> tuple[int, int]:
    """Метод для получения сегодняшнего дня и недели"""

    day = int(f"{datetime.now(TZ).weekday() + 1}")
    week_int = 2 if NUMERATOR == 0 else 1
    week = week_int if datetime.now(TZ).isocalendar()[1] % 2 == 0 else 3 - week_int
    if day == 7:
        return 1, week + 1 if week == 1 else week - 1

    else:
        return day, week


def time_to_minutes(time_str: str) -> int:
    """Метод для перевода времени в минуты"""

    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes


def get_time_symbol(start_time: str) -> str:
    """Метод для получения эмодзи часов с указанным временем времени"""

    hour = int(start_time.split(":")[0])
    if 8 <= hour < 10:
        return "🕣 "
    elif 10 <= hour < 12:
        return "🕙 "
    elif 12 <= hour < 13:
        return "🕛 "
    elif 13 <= hour < 14:
        return "🕜 "
    elif 14 <= hour < 16:
        return "🕞 "
    elif 16 <= hour < 18:
        return "🕔 "
    elif 18 <= hour < 20:
        return "🕡 "
    else:
        return "🕙 "


def get_lesson_label(subject: str) -> str:
    """Метод для получения типа пары по его сокращению"""

    if "пр" in subject.lower():
        return "Практика"
    elif "пр." in subject.lower():
        return "Практика"
    elif "лаб" in subject.lower():
        return "Лабораторные"
    elif "лаб." in subject.lower():
        return "Лабораторные"
    elif "л" in subject.lower():
        return "Лекция"
    elif "л." in subject.lower():
        return "Лекция"
    elif ("курс" or "кур/проект" or "кур/проек.") in subject.lower():
        return "Курсовой проект"
    else:
        return ""


def create_progress_bar(completed: int, total: int) -> str:
    total_blocks = 20
    filled_blocks = int((completed / total) * total_blocks)
    bar = "■" * filled_blocks + "□" * (total_blocks - filled_blocks)
    return f"[{bar}]"


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


from datetime import datetime
import logging

from app.config import TZ, LOG_LEVEL, LOG_FILE


def set_logging(logger: str):
    logging.Formatter.converter = lambda *args: datetime.now(TZ).timetuple()
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARN,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
        "EXCEPTION": logging.ERROR
    }
    logging.basicConfig(
        level=levels[LOG_LEVEL],
        format="%(asctime)s %(levelname)s [%(funcName)s] %(message)s",
        datefmt="%H:%M:%S %d-%m-%Y",
        handlers=[
            logging.FileHandler(
                LOG_FILE,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ],
        force=True
    )
    logging.getLogger(logger).setLevel(levels[LOG_LEVEL])
