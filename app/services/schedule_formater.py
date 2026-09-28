import re

from app.core.constants import DAY_NAMES, LESSON_LABELS, LESSON_TIME, TIME_SYMBOLS
from app.core.enums import WeekType
from app.schemas.schedule import ScheduleEntry


class ScheduleFormatterService:
    LESSON_PATTERN = re.compile(r"\([^)]*\)", re.IGNORECASE)
    LESSON_TYPE_PATTERN = re.compile(r"\(([^)]*)\)", re.IGNORECASE)

    @staticmethod
    def get_time_symbol(start_time: str) -> str:
        """Метод для получения эмодзи часов с указанным временем времени"""

        hour = int(start_time.split(":", maxsplit=1)[0])
        for limit, symbol in TIME_SYMBOLS:
            if hour == limit:
                return symbol

        return "🕙"

    @staticmethod
    def get_lesson_label(subject: str) -> str:
        """Получить тип пары по сокращению."""

        subject = subject.lower()

        for patterns, label in LESSON_LABELS:
            if any(pattern in subject for pattern in patterns):
                return label

        return ""

    @staticmethod
    def _header(title: str, day: int, week: WeekType) -> str:
        week_name = "Числитель" if week == WeekType.ODD else "Знаменатель"
        return f"{DAY_NAMES[day]}       {week_name}\n{title}\n\n"

    def group(self, group_name: str, day_of_week: int, week_type: WeekType, entries: list[ScheduleEntry]) -> str:
        if not entries:
            return ScheduleFormatterService._header(group_name, day_of_week, week_type) + "Сегодня пар нет!"

        text = ScheduleFormatterService._header(group_name, day_of_week, week_type)

        for e in entries:
            subject = re.sub(self.LESSON_PATTERN, "", e.subject).strip()
            label = self.get_lesson_label(str(re.search(self.LESSON_TYPE_PATTERN, e.subject)))
            time = LESSON_TIME[e.lesson_number]
            text += (
                f"{self.get_time_symbol(time)} {time}   {label}\n"
                f"📖 {subject}\n"
                f"{f'👫 Подгруппа: {e.subgroup}\n' if e.subgroup else ''}"
                f"👨‍🏫 {e.teacher}\n"
                f"🏠 {e.room}\n\n"
            )

        return text

    def teacher(self, *, teacher_name: str, day_of_week: int, week_type: WeekType, entries: list[ScheduleEntry]) -> str:
        if not entries:
            return ScheduleFormatterService._header(teacher_name, day_of_week, week_type) + "Сегодня пар нет!"

        text = ScheduleFormatterService._header(teacher_name, day_of_week, week_type)

        for e in entries:
            subject = re.sub(self.LESSON_PATTERN, "", e.subject).strip()
            label = self.get_lesson_label(str(re.search(self.LESSON_TYPE_PATTERN, e.subject)))
            time = LESSON_TIME[e.lesson_number]

            text += (
                f"{self.get_time_symbol(time)} {time}   {label}\n"
                f"📖 {subject}\n"
                f"👫 {e.group}\n"
                f"{f'🧍🏼 Подгруппа: {e.subgroup}\n' if e.subgroup else ''}"
                f"🏠 {e.room}\n\n"
            )
        return text

    def room(self, *, room_name: str, day_of_week: int, week_type: WeekType, entries: list[ScheduleEntry]):
        if not entries:
            return ScheduleFormatterService._header(room_name, day_of_week, week_type) + "Сегодня пар нет!"

        text = ScheduleFormatterService._header(room_name, day_of_week, week_type)

        for e in entries:
            subject = re.sub(self.LESSON_PATTERN, "", e.subject).strip()
            label = self.get_lesson_label(str(re.search(self.LESSON_TYPE_PATTERN, e.subject)))
            time = LESSON_TIME[e.lesson_number]

            subroom = " "
            if e.room != room_name:
                prefix = e.room[-2]
                subroom = f"|{prefix}|"

            text += (
                f"{self.get_time_symbol(time)} {time}   {subroom}   {label}\n"
                f"📖 {subject}\n"
                f"👫 {e.group}\n"
                f"{f'🧍🏼 Подгруппа: {e.subgroup}\n' if e.subgroup else ''}"
                f"👨‍🏫 {e.teacher}\n\n"
            )

        return text
