from aiogram.filters.callback_data import CallbackData

from app.core.enums import Keyboard, WeekType


class ChangeCallbackFactory(CallbackData, prefix="start"):
    """Фабрика для создания CallbackData для клавиатур выбора преподавателя, группы или аудитории."""

    action: str | None
    value: int


class DayCallbackFactory(CallbackData, prefix="common"):
    """Фабрика для создания CallbackData для клавиатур изменения дня или недели."""

    action: str | None = None
    value: int
    day: int | None = None
    week: WeekType | None = None
    keyboard: Keyboard | None = None


class DefaultChangeCallbackFactory(CallbackData, prefix="default"):
    """Фабрика для создания CallbackData для клавиатур выбора преподавателя, группы или аудитории."""

    action: str | None = None
    value: int
