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

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import config
from bot.database.user import UserDatabase
from bot.markups import keyboard_factory

student_menu = [
    [KeyboardButton(text="Расписание на сегодня")],
    [KeyboardButton(text="Группы"), KeyboardButton(text="Преподаватели")],
]
teacher_menu = [
    [KeyboardButton(text="Расписание на сегодня")],
    [
        KeyboardButton(text="Группы"),
        KeyboardButton(text="Преподаватели"),
        KeyboardButton(text="Кабинеты"),
    ],
]


student_menu = ReplyKeyboardMarkup(keyboard=student_menu, resize_keyboard=True)
teacher_menu = ReplyKeyboardMarkup(keyboard=teacher_menu, resize_keyboard=True)


def get_teachers():
    """Возвращает клавиатуру с преподавателями, указанными в config.toml."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for teacher in config.TEACHERS:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="teacher", value=Schedule().get_teacher_id(teacher)
            ),
        )
    builder.adjust(2)
    return builder.as_markup()


def get_groups():
    """Возвращает клавиатуру с группами, указанными в config.toml."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for group in config.GROUPS:
        builder.button(
            text=group,
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="group", value=Schedule().get_group_id(group)
            ),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_rooms():
    """Возвращает клавиатуру с аудиториями, указанными в config.toml."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for room in config.ROOMS:
        builder.button(
            text=str(room),
            callback_data=keyboard_factory.ChangeCallbackFactory(
                action="room", value=Schedule().get_room_id(room)
            ),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_default_teachers():
    """Возвращает клавиатуру с преподавателями, указанными в config.toml."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for teacher in config.ALL_PERSONAL:
        builder.button(
            text=str(teacher),
            callback_data=keyboard_factory.DefaultChangeCallbackFactory(
                action="default_teacher", value=Schedule().get_teacher_id(teacher)
            ),
        )
    builder.button(
        text="Очистить",
        callback_data=keyboard_factory.DefaultChangeCallbackFactory(
            action="default_teacher", value=None
        ),
    )
    builder.adjust(2)
    return builder.as_markup()


def get_default_groups():
    """Возвращает клавиатуру с группами, указанными в config.toml."""

    from bot.database.schedule import Schedule

    builder = InlineKeyboardBuilder()
    for group in config.GROUPS:
        builder.button(
            text=group,
            callback_data=keyboard_factory.DefaultChangeCallbackFactory(
                action="default_group", value=Schedule().get_group_id(group)
            ),
        )
    builder.button(
        text="Очистить",
        callback_data=keyboard_factory.DefaultChangeCallbackFactory(
            action="default_group", value=None
        ),
    )
    builder.adjust(3)
    return builder.as_markup()


def get_days(user_id: int, keyboard_type: str, week: int, value: int):
    """Возвращает клавиатуру с днями недели и кнопкой смены недели."""

    builder = InlineKeyboardBuilder()
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]:
        int_day = {"Пн": 1, "Вт": 2, "Ср": 3, "Чт": 4, "Пт": 5, "Сб": 6}[day]
        builder.button(
            text=day,
            callback_data=keyboard_factory.DayCallbackFactory(
                action="day",
                keyboard_type=keyboard_type,
                day=int_day,
                week=week,
                value=value,
            ),
        )
    if week == 1:
        builder.button(
            text="✅ Числитель",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
        builder.button(
            text="Знаменатель ➡️",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="week",
                keyboard_type=keyboard_type,
                week=2,
                day=UserDatabase(user_id).day,
                value=value,
            ),
        )
    elif week == 2:
        builder.button(
            text="✅ Знаменатель",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
        builder.button(
            text="Числитель ➡️",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="week",
                keyboard_type=keyboard_type,
                week=1,
                day=UserDatabase(user_id).day,
                value=value,
            ),
        )
    else:
        builder.button(
            text="Неизвестная неделя",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
    builder.adjust(3)
    return builder.as_markup()


def get_days_teacher(user_id: int, keyboard_type: str, week: int, value: int):
    """Возвращает клавиатуру с днями недели и кнопкой смены недели."""

    from bot.database.user import UserDatabase

    builder = InlineKeyboardBuilder()
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]:
        int_day = {"Пн": 1, "Вт": 2, "Ср": 3, "Чт": 4, "Пт": 5, "Сб": 6}[day]
        builder.button(
            text=str(day),
            callback_data=keyboard_factory.DayCallbackFactory(
                action="day",
                keyboard_type=keyboard_type,
                day=int_day,
                week=week,
                value=value,
            ),
        )
    if week == 1:
        builder.button(
            text="✅ Числитель",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
        # builder.button(
        #     text="✏ Изменить ",
        #     callback_data=keyboard_factory.DayCallbackFactory(
        #         action="schedule_editing",
        #         day=UserDatabase(user_id).day,
        #         value=value,
        #         keyboard_type=keyboard_type,
        #     ),
        # )
        builder.button(
            text="Знаменатель ➡️",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="week",
                keyboard_type=keyboard_type,
                week=2,
                day=UserDatabase(user_id).day,
                value=value,
            ),
        )
    elif week == 2:
        builder.button(
            text="✅ Знаменатель",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
        # builder.button(
        #     text="✏ Изменить ",
        #     callback_data=keyboard_factory.DayCallbackFactory(
        #         action="schedule_editing",
        #         day=UserDatabase(user_id).day,
        #         value=value,
        #         keyboard_type=keyboard_type,
        #     ),
        # )
        builder.button(
            text="Числитель ➡",
            callback_data=keyboard_factory.DayCallbackFactory(
                action="week",
                keyboard_type=keyboard_type,
                week=1,
                day=UserDatabase(user_id).day,
                value=value,
            ),
        )
    else:
        builder.button(
            text="Неизвестная неделя",
            callback_data=keyboard_factory.DayCallbackFactory(action="ignore"),
        )
    builder.adjust(3)
    return builder.as_markup()
