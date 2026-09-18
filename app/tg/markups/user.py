from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.config import config
from app.core.constants import DAYS_SHORT
from app.core.enums import Keyboard, UserRole, WeekType
from app.schemas.keyboard import keyboard_data
from app.tg.markups import keyboard_factory


def student_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Расписание на сегодня")],
            [KeyboardButton(text="Группы"), KeyboardButton(text="Преподаватели")],
        ],
        resize_keyboard=True,
    )


def teacher_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Расписание на сегодня")],
            [
                KeyboardButton(text="Группы"),
                KeyboardButton(text="Преподаватели"),
                KeyboardButton(text="Кабинеты"),
            ],
        ],
        resize_keyboard=True,
    )


def get_teachers() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с преподавателями, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    for teacher in sorted(config.teachers, key=str):
        builder.button(
            text=teacher,
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="teacher",
                value=keyboard_data.teacher_ids[teacher],
            ),
        )
    builder.adjust(2)
    return builder.as_markup()


def get_groups() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с группами, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    counter = 0

    for group in config.groups:
        if group == "-":
            counter += 1
            builder.button(
                text=group, callback_data=keyboard_factory.ChangeCallbackFactory(action=f"ignore{counter}", value=0)
            )
        else:
            builder.button(
                text=group,
                callback_data=keyboard_factory.ChangeCallbackFactory(
                    action="group",
                    value=keyboard_data.group_ids[group],
                ),
            )
    builder.adjust(3)
    return builder.as_markup()


def get_rooms() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с аудиториями, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    for room in config.rooms:
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="room",
                value=keyboard_data.room_ids[room],
            ),
        )
    builder.adjust(3)
    return builder.as_markup()


async def get_default_teachers() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с преподавателями, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    for teacher in config.all_personal:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.DefaultChangeCallbackFactory(
                action="default_teacher",
                value=keyboard_data.teacher_ids[teacher],
            ),
        )
    builder.button(
        text="Очистить",
        callback_data=keyboard_factory.DefaultChangeCallbackFactory(action="default_teacher", value=0),
    )
    builder.adjust(2)
    return builder.as_markup()


def get_default_groups() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с группами, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    counter = 0

    for group in config.groups:
        if group == "-":
            counter += 1
            builder.button(
                text=group, callback_data=keyboard_factory.ChangeCallbackFactory(action=f"ignore{counter}", value=0)
            )
        else:
            builder.button(
                text=group,
                callback_data=keyboard_factory.DefaultChangeCallbackFactory(
                    action="default_group",
                    value=keyboard_data.teacher_ids[group],
                ),
            )
    builder.button(
        text="Очистить",
        callback_data=keyboard_factory.DefaultChangeCallbackFactory(action="default_group", value=0),
    )
    builder.adjust(3)
    return builder.as_markup()


def get_days(keyboard: Keyboard, week: WeekType, day: int, value: int) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с днями недели и кнопкой смены недели."""

    builder = InlineKeyboardBuilder()

    for day_enum, day_short in DAYS_SHORT.items():
        builder.button(
            text=day_short,
            callback_data=keyboard_factory.DayCallbackFactory(
                action="day",
                keyboard=keyboard,
                day=day_enum.value,
                week=week,
                value=value,
            ),
        )
    if week == WeekType.ODD:
        active_week_text = "✅ Числитель"
        next_week = WeekType.EVEN
        next_week_text = "Знаменатель ➡️"
    elif week == WeekType.EVEN:
        active_week_text = "✅ Знаменатель"
        next_week = WeekType.ODD
        next_week_text = "Числитель ➡️"
    else:
        active_week_text = "Неизвестная неделя"
        next_week = week
        next_week_text = "Неизвестная неделя"

    builder.button(
        text=active_week_text,
        callback_data=keyboard_factory.DayCallbackFactory(action="ignore", value=0),
    )

    builder.button(
        text=next_week_text,
        callback_data=keyboard_factory.DayCallbackFactory(
            action="week",
            keyboard=keyboard,
            week=next_week,
            day=day,
            value=value,
        ),
    )

    builder.adjust(3)
    return builder.as_markup()


def get_sheets(user_role: UserRole) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с днями недели и кнопкой смены недели."""

    builder = InlineKeyboardBuilder()
    builder.button(
        text="Преподаватель",
        callback_data=keyboard_factory.ChangeCallbackFactory(action="teacher_sheet", value=0),
    )
    builder.button(
        text="Группа",
        callback_data=keyboard_factory.ChangeCallbackFactory(action="group_sheet", value=0),
    )
    if user_role == UserRole.TEACHER:
        builder.button(
            text="Кабинет",
            callback_data=keyboard_factory.ChangeCallbackFactory(action="room_sheet", value=0),
        )
    builder.adjust(2)
    return builder.as_markup()


def get_sheet_teachers() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с преподавателями, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    for teacher in sorted(config.teachers, key=str):
        builder.button(
            text=teacher,
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="teacher_sheet",
                value=keyboard_data.teacher_ids[teacher],
            ),
        )
    builder.adjust(2)
    return builder.as_markup()


def get_sheet_groups(user_role: UserRole) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с группами, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    counter = 0
    for group in config.groups:
        if group == "-":
            counter += 1
            builder.button(
                text=group,
                callback_data=keyboard_factory.ChangeCallbackFactory(action=f"ignore{counter}", value=0),
            )
        else:
            builder.button(
                text=group,
                callback_data=keyboard_factory.ChangeCallbackFactory(
                    action="group_sheet",
                    value=keyboard_data.group_ids[group],
                ),
            )
    builder.adjust(3)
    if user_role == UserRole.TEACHER:
        rows = [len(row) for row in builder.as_markup().inline_keyboard]
        rows.append(1)
        builder.button(
            text="Все и сразу",
            callback_data=keyboard_factory.ChangeCallbackFactory(action="group_sheet", value=9999),
        )
        builder.adjust(*rows)
    return builder.as_markup()


def get_sheet_rooms() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с аудиториями, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    for room in config.rooms:
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="room_sheet",
                value=keyboard_data.room_ids[room],
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(
        text="Все и сразу",
        callback_data=keyboard_factory.ChangeCallbackFactory(action="room_sheet", value=9999),
    )
    builder.adjust(*rows)
    return builder.as_markup()
