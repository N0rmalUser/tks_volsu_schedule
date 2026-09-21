from datetime import time
from pathlib import Path
from zoneinfo import ZoneInfo

from app.core.config import config
from app.core.enums import DayOfWeek, WeekType
from app.schemas.schedule import LessonTime


# ===== TIMEZONE =====
TZ: ZoneInfo = ZoneInfo(config.timezone)

# ===== PATHS =====
ROOT_PATH = Path(__file__).resolve().parent.parent.parent

DATA_PATH = ROOT_PATH / "data"
GROUPS_SCHEDULE_PATH = DATA_PATH / "groups"
TEACHERS_SHEETS_PATH = DATA_PATH / "teachers"
ROOMS_SHEETS_PATH = DATA_PATH / "rooms"

PLOT_PATH = DATA_PATH / "plot"

TIME_SYMBOLS = {(8, "🕣"), (10, "🕙"), (12, "🕛"), (13, "🕜"), (15, "🕞"), (17, "🕔"), (18, "🕡")}

LESSON_LABELS = (
    (("пр", "пр."), "Практика"),
    (("лаб", "лаб."), "Лабораторные"),
    (("курс", "кур/проект", "кур/проек."), "Курсовой проект"),
    (("л", "л."), "Лекция"),
)

LESSON_TIME = {
    1: "08:30-10:00",
    2: "10:10-11:40",
    3: "12:00-13:30",
    4: "13:40-15:10",
    5: "15:20-16:50",
    6: "17:00-18:30",
    7: "18:40-20:10",
}

DAY_NAMES = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
}

DAYS_OF_WEEK = {
    "понедельник": 1,
    "вторник": 2,
    "среда": 3,
    "четверг": 4,
    "пятница": 5,
    "суббота": 6,
}

LESSONS: tuple[LessonTime, ...] = (
    LessonTime(1, time(8, 30), time(10, 0)),
    LessonTime(2, time(10, 10), time(11, 40)),
    LessonTime(3, time(12, 0), time(13, 30)),
    LessonTime(4, time(13, 40), time(15, 10)),
    LessonTime(5, time(15, 20), time(16, 50)),
    LessonTime(6, time(17, 0), time(18, 30)),
    LessonTime(7, time(18, 40), time(20, 10)),
)

LESSON_BY_START_TIME: dict[time, int] = {lesson.start: lesson.number for lesson in LESSONS}

WEEK_MAP = {
    1: WeekType.ODD,
    2: WeekType.EVEN,
}

DAYS_SHORT = {
    DayOfWeek.MONDAY: "Пн",
    DayOfWeek.TUESDAY: "Вт",
    DayOfWeek.WEDNESDAY: "Ср",
    DayOfWeek.THURSDAY: "Чт",
    DayOfWeek.FRIDAY: "Пт",
    DayOfWeek.SATURDAY: "Сб",
}
