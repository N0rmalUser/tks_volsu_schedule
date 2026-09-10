import re

from app.core.constants import DAY_NAMES, LESSON_LABELS, LESSON_TIME, TIME_SYMBOLS
from app.core.enums import WeekType
from app.schemas.schedule import ScheduleEntry


def get_time_symbol(start_time: str) -> str:
    """Метод для получения эмодзи часов с указанным временем времени"""

    hour = int(start_time.split(":", maxsplit=1)[0])
    for limit, symbol in TIME_SYMBOLS:
        if hour == limit:
            return symbol

    return "🕙"


def get_lesson_label(subject: str) -> str:
    """Получить тип пары по сокращению."""

    subject = subject.lower()

    for patterns, label in LESSON_LABELS:
        if any(pattern in subject for pattern in patterns):
            return label

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
