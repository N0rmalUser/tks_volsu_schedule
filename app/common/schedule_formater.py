import re

from app.schemas.enums import WeekType
from app.schemas.schedule import ScheduleEntry


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


def get_time_symbol(start_time: str) -> str:
    """Метод для получения эмодзи часов с указанным временем времени"""

    hour = int(start_time.split(":")[0])
    if 8 <= hour < 10:
        return "🕣"
    if 10 <= hour < 12:
        return "🕙"
    if 12 <= hour < 13:
        return "🕛"
    if 13 <= hour < 14:
        return "🕜"
    if 14 <= hour < 16:
        return "🕞"
    if 16 <= hour < 18:
        return "🕔"
    if 18 <= hour < 20:
        return "🕡"
    return "🕙"


def get_lesson_label(subject: str) -> str:
    """Метод для получения типа пары по его сокращению"""
    subject = subject.lower()
    if "пр" in subject:
        return "Практика"
    if "пр." in subject:
        return "Практика"
    if "лаб" in subject:
        return "Лабораторные"
    if "лаб." in subject:
        return "Лабораторные"
    if "л" in subject:
        return "Лекция"
    if "л." in subject:
        return "Лекция"
    if any(phrase in subject for phrase in ("курс", "кур/проект", "кур/проек.")):
        return "Курсовой проект"
    return ""


class ScheduleFormatter:
    @staticmethod
    def _header(title: str, day: int, week: WeekType) -> str:
        week_name = "Числитель" if week == WeekType.ODD else "Знаменатель"
        return f"{DAY_NAMES[day]}       {week_name}\n{title}\n\n"

    @staticmethod
    def group(day_of_week: int, week_type: WeekType, entries: tuple[str, list[ScheduleEntry]]) -> str:
        group_name, schedule_entries = entries
        if not schedule_entries:
            return ScheduleFormatter._header(group_name, day_of_week, week_type) + "Сегодня пар нет!"

        text = ScheduleFormatter._header(group_name, day_of_week, week_type)

        for e in schedule_entries:
            subject = re.sub(r"\([^)]*\)", "", e.subject).strip()
            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", e.subject)))
            time = LESSON_TIME[e.lesson_number]
            text += (
                f"{get_time_symbol(time)} {time}   {label}\n"
                f"📖 {subject}\n"
                f"{f'👫 Подгруппа: {e.subgroup}\n' if e.subgroup else ''}"
                f"👨‍🏫 {e.teacher}\n"
                f"🏠 {e.room}\n\n"
            )

        return text

    @staticmethod
    def teacher(*, day_of_week, week_type, entries):
        teacher_name, entries = entries
        if not entries:
            return ScheduleFormatter._header(teacher_name, day_of_week, week_type) + "Сегодня пар нет!"

        text = ScheduleFormatter._header(teacher_name, day_of_week, week_type)
        for e, is_teacher_entry in entries:
            subject = re.sub(r"\([^)]*\)", "", e.subject).strip()
            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", e.subject)))
            time = LESSON_TIME[e.lesson_number]

            if is_teacher_entry:
                text += (
                    f"{get_time_symbol(time)} {time}   {label}\n"
                    f"📖 {subject}\n"
                    f"👫 {e.group}\n"
                    f"{f'🧍🏼 Подгруппа: {e.subgroup}\n' if e.subgroup else ''}"
                    f"🏠 {e.room}\n\n"
                )
            else:
                text += f"{get_time_symbol(time)} {time}   {label}\n📖 {subject}\n👨‍🏫 {e.teacher}\n🏠 {e.room}\n\n"
        return text

    @staticmethod
    def room(*, day_of_week, week_type, entries):
        room_name, entries = entries
        if not entries:
            return ScheduleFormatter._header(room_name, day_of_week, week_type) + "Сегодня пар нет!"

        text = ScheduleFormatter._header(room_name, day_of_week, week_type)

        for e in entries:
            subject = re.sub(r"\([^)]*\)", "", e.subject).strip()
            label = get_lesson_label(str(re.search(r"\(([^)]*)\)", e.subject)))
            time = LESSON_TIME[e.lesson_number]

            subroom = " "
            if e.room != room_name:
                prefix = e.room[-2]
                subroom = f"|{prefix}|"

            text += (
                f"{get_time_symbol(time)} {time}   {subroom}   {label}\n"
                f"📖 {subject}\n"
                f"👫 {e.group}\n"
                f"{f'🧍🏼 Подгруппа: {e.subgroup}\n' if e.subgroup else ''}"
                f"👨‍🏫 {e.teacher}\n\n"
            )

        return text
