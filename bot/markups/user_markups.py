from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.markups import keyboard_factory
import config


student_menu = [
    [
        KeyboardButton(text="Расписание на сегодня")
    ], [
        KeyboardButton(text="Группы")
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
    builder = InlineKeyboardBuilder()
    for teacher in config.teachers:
        builder.button(text=str(teacher), callback_data=keyboard_factory.ChangeCallbackFactory(action="teacher", value=str(teacher)))
    builder.adjust(2)
    return builder.as_markup()


def get_groups():
    builder = InlineKeyboardBuilder()
    for group in config.groups:
        builder.button(text=str(group), callback_data=keyboard_factory.ChangeCallbackFactory(action="group", value=str(group)))
    builder.adjust(4)
    return builder.as_markup()


def get_rooms():
    builder = InlineKeyboardBuilder()
    for room in config.rooms:
        builder.button(text=str(room), callback_data=keyboard_factory.ChangeCallbackFactory(action="room", value=room))
    builder.adjust(3)
    return builder.as_markup()


def get_days(type: str, week: int):
    builder = InlineKeyboardBuilder()
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]:
        int_day = {"Пн": '1', "Вт": '2', "Ср": '3', "Чт": '4', "Пт": '5', "Сб": '6'}[day]
        builder.button(text=str(day), callback_data=keyboard_factory.DayCallbackFactory(action='day', value=int_day, call_type=type))
    if week == 1:
        builder.button(text="✅ Числитель", callback_data=keyboard_factory.DayCallbackFactory(action='ignore'))
        builder.button(text="Знаменатель ➡️", callback_data=keyboard_factory.DayCallbackFactory(action="week", value='2', call_type=type))
    elif week == 2:
        builder.button(text="✅ Знаменатель", callback_data=keyboard_factory.DayCallbackFactory(action='ignore'))
        builder.button(text="Числитель ➡️", callback_data=keyboard_factory.DayCallbackFactory(action='week', value='1', call_type=type))
    else:
        builder.button(text='Неизвестная неделя', callback_data=keyboard_factory.DayCallbackFactory(action='ignore'))
    builder.adjust(3)
    return builder.as_markup()
