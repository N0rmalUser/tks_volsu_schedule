from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ChangeCallbackFactory(CallbackData, prefix="start_change"):
    """Фабрика для создания CallbackData для клавиатур выбора преподавателя, группы или аудитории."""

    action: Optional[str] = None
    value: Optional[int] = None


class DayCallbackFactory(CallbackData, prefix="day_change"):
    """Фабрика для создания CallbackData для клавиатур изменения дня или недели."""

    action: Optional[str] = None
    value: Optional[int] = None
    day: Optional[int] = None
    week: Optional[int] = None
    keyboard_type: Optional[str] = None


class DefaultChangeCallbackFactory(CallbackData, prefix="default_change"):
    """Фабрика для создания CallbackData для клавиатур выбора преподавателя, группы или аудитории."""

    action: Optional[str] = None
    value: Optional[int] = None


class ScheduleEditingCallbackFactory(CallbackData, prefix="edit"):
    """Фабрика для создания CallbackData для клавиатур изменения расписания."""

    action: Optional[str] = None
    value: Optional[int] = None
    day: Optional[int] = None
    edit: Optional[str] = None
    schedule_id: Optional[int] = None
    keyboard_type: Optional[str] = None
