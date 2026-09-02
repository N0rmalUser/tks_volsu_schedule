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

from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.config import config
from app.schemas.enums import DayOfWeek, Keyboard, UserRole, WeekType
from app.services.schedule import ScheduleService
from app.tg.markups import keyboard_factory


DAYS_SHORT = {
    DayOfWeek.MONDAY: "Пн",
    DayOfWeek.TUESDAY: "Вт",
    DayOfWeek.WEDNESDAY: "Ср",
    DayOfWeek.THURSDAY: "Чт",
    DayOfWeek.FRIDAY: "Пт",
    DayOfWeek.SATURDAY: "Сб",
}


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
    for index, teacher in enumerate(sorted(config.teachers), start=1):
        builder.button(
            text=str(teacher), callback_data=keyboard_factory.ChangeCallbackFactory(action="teacher", value=index)
        )
    builder.adjust(2)
    return builder.as_markup()


def get_groups() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с группами, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    counter = 0
    groups = config.groups
    sorted_groups = sorted([group for group in groups if group != "-"])
    for group in groups:
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
                    value=sorted_groups.index(group) + 1,
                ),
            )
    builder.adjust(3)
    return builder.as_markup()


def get_rooms() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с аудиториями, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    rooms = config.rooms
    for index, room in enumerate(rooms, start=1):
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ChangeCallbackFactory(action="room", value=index),
        )
    builder.adjust(3)
    return builder.as_markup()


async def get_default_teachers() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с преподавателями, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    all_personal_ids = await ScheduleService().get_teacher_ids()
    for teacher in config.all_personal:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.DefaultChangeCallbackFactory(
                action="default_teacher",
                value=all_personal_ids[teacher],
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
    groups = config.groups
    sorted_groups = sorted([group for group in groups if group != "-"])
    for group in groups:
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
                    value=sorted_groups.index(group) + 1,
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
    for index, teacher in enumerate(config.teachers, start=1):
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="teacher_sheet",
                value=index,
            ),
        )
    builder.adjust(2)
    return builder.as_markup()


def get_sheet_groups(user_role: UserRole) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с группами, указанными в конфиге."""

    builder = InlineKeyboardBuilder()
    counter = 0
    for index, group in enumerate(config.groups, start=1):
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
                    value=index,
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
    for index, room in enumerate(config.rooms, start=1):
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="room_sheet",
                value=index,
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
