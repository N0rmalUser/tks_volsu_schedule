from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import config

from bot import database as db
from bot.markups import keyboard_factory
from aiogram.utils.keyboard import InlineKeyboardBuilder


student_menu = [
    [
        KeyboardButton(text="Расписание на сегодня")
    ], [
        KeyboardButton(text="Группы"),
        KeyboardButton(text="Преподаватели")
    ]
]
teacher_menu = [
    [
        KeyboardButton(text="Расписание на сегодня")
    ], [
        KeyboardButton(text="Группы"),
        KeyboardButton(text="Преподаватели"),
        KeyboardButton(text="Кабинеты")
    ]
]


student_menu = ReplyKeyboardMarkup(keyboard=student_menu, resize_keyboard=True)
teacher_menu = ReplyKeyboardMarkup(keyboard=teacher_menu, resize_keyboard=True)


def get_teachers():
    """Возвращает клавиатуру с преподавателями, указанными в config.py."""
    builder = InlineKeyboardBuilder()
    for teacher in config.teachers:
        builder.button(text=str(teacher), callback_data=keyboard_factory.ChangeCallbackFactory(action="teacher", value=str(teacher)))
    builder.adjust(2)
    return builder.as_markup()


def get_groups():
    """Возвращает клавиатуру с группами, указанными в config.py."""
    builder = InlineKeyboardBuilder()
    for group in config.groups:
        builder.button(text=group, callback_data=keyboard_factory.ChangeCallbackFactory(action="group", value=group))
    builder.adjust(4)
    return builder.as_markup()


def get_rooms():
    """Возвращает клавиатуру с аудиториями, указанными в config.py."""
    builder = InlineKeyboardBuilder()
    for room in config.rooms:
        builder.button(text=str(room), callback_data=keyboard_factory.ChangeCallbackFactory(action="room", value=room))
    builder.adjust(3)
    return builder.as_markup()


def get_days(user_id: int, keyboard_type: str, week: int, value: str):
    """Возвращает клавиатуру с днями недели и кнопкой смены недели."""
    builder = InlineKeyboardBuilder()
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]:
        int_day = {"Пн": 1, "Вт": 2, "Ср": 3, "Чт": 4, "Пт": 5, "Сб": 6}[day]
        builder.button(text=str(day), callback_data=keyboard_factory.DayCallbackFactory(action='day', keyboard_type=keyboard_type, day=int_day, week=week, value=value))
    if week == 1:
        builder.button(text="✅ Числитель", callback_data=keyboard_factory.DayCallbackFactory(action='ignore'))
        builder.button(text="Знаменатель ➡️", callback_data=keyboard_factory.DayCallbackFactory(action="week", keyboard_type=keyboard_type, week=2, day=db.get_day(user_id), value=value))
    elif week == 2:
        builder.button(text="✅ Знаменатель", callback_data=keyboard_factory.DayCallbackFactory(action='ignore'))
        builder.button(text="Числитель ➡️", callback_data=keyboard_factory.DayCallbackFactory(action='week', keyboard_type=keyboard_type, week=1, day=db.get_day(user_id), value=value))
    else:
        builder.button(text='Неизвестная неделя', callback_data=keyboard_factory.DayCallbackFactory(action='ignore'))
    builder.adjust(3)
    return builder.as_markup()
