from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.database.user import UserDatabase
from bot.markups import user_markups as kb
from bot.markups.keyboard_factory import ChangeCallbackFactory, DayCallbackFactory, DefaultChangeCallbackFactory
from bot.misc import text_maker

import importlib

import logging

router = Router()


@router.callback_query(DayCallbackFactory.filter(F.action == "ignore"))
async def ignore_handler(callback: CallbackQuery) -> None:
    """Функция, сбрасывающая нажатия кнопки без функционала."""

    await callback.answer("Сейчас эта неделя")


@router.callback_query(DayCallbackFactory.filter(F.action == "day"))
async def day_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки дня недели. Отправляет расписание на этот день для преподов, групп и аудиторий."""
    keyboard_type: str = callback_data.keyboard_type
    value: str = callback_data.value
    week: int = callback_data.week
    day: int = callback_data.day

    user = UserDatabase(callback.from_user.id)

    if callback_data.day == user.day:
        await callback.answer()
        return
    user.day = callback_data.day

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(day=day, week=week, teacher_name=value)
        week_kb = kb.get_days(callback.from_user.id, keyboard_type='teacher', week=week, value=value)
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(day=day, week=week, group_name=value)
        week_kb = kb.get_days(callback.from_user.id, keyboard_type='group', week=week, value=value)
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(day=day, week=week, room_name=value)
        week_kb = kb.get_days(callback.from_user.id, keyboard_type='room', week=week, value=value)
    else:
        logging.error(f"{callback.from_user.id} сделал неизвестный callback (teacher, group, room): {callback.data} в _week_day_handler")
        await callback.answer("Неизвестный тип запроса. Напишите админу /admin")
        return

    await callback.message.edit_text(text, reply_markup=week_kb)

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(DayCallbackFactory.filter(F.action == "week"))
async def week_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки недели. Отправляет расписание на следующую неделю для преподов, групп и аудиторий, сохраняя день."""

    keyboard_type = callback_data.keyboard_type
    value = callback_data.value
    week = 1 if int(callback_data.week) != 2 else 2
    day = callback_data.day

    user = UserDatabase(callback.from_user.id)

    if callback_data.day == str(user.day):
        await callback.answer()
        return
    user.set_day = callback_data.day

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(day=day, week=week, teacher_name=value)
        week_kb = kb.get_days(callback.from_user.id, keyboard_type='teacher', week=week, value=value)
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(day=day, week=week, group_name=value)
        week_kb = kb.get_days(callback.from_user.id, keyboard_type='group', week=week, value=value)
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(day=day, week=week, room_name=value)
        week_kb = kb.get_days(callback.from_user.id, keyboard_type='room', week=week, value=value)
    else:
        logging.error(f"{callback.from_user.id} сделал неизвестный callback (teacher, group, room): {callback.data} в _week_day_handler")
        await callback.answer("Неизвестный тип запроса. Напишите админу /admin")
        return

    await callback.message.edit_text(text, reply_markup=week_kb)

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "room"))
async def room_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки аудитории. Отправляет расписание на этот день для аудитории."""

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()
    await callback.message.edit_text(text_maker.get_room_schedule(day=user.day, week=user.week, room_name=callback_data.value),
                                     reply_markup=kb.get_days(callback.from_user.id, keyboard_type='room', week=user.week, value=callback_data.value))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == 'teacher'))
async def teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки преподавателя. Отправляет расписание на этот день для преподавателя.
    Если преподаватель является учеником (указывается в config.py), отправляет расписание его групп, смешанное с занятиями, которые он сам проводит
    """

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()
    user.teacher = callback_data.value
    await callback.message.edit_text(text_maker.get_teacher_schedule(day=user.day, week=user.week,
                                                                     teacher_name=callback_data.value),
                                     reply_markup=kb.get_days(callback.from_user.id, keyboard_type='teacher',
                                                              week=user.week, value=callback_data.value))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == 'group'))
async def group_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки группы. Отправляет расписание на этот день для группы."""

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()
    user.group = callback_data.value
    await callback.message.edit_text(text_maker.get_group_schedule(day=user.day, week=user.week,
                                                                   group_name=callback_data.value),
                                     reply_markup=kb.get_days(callback.from_user.id, keyboard_type='group', week=user.week,
                                                              value=callback_data.value))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == 'default_teacher'))
async def default_teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    user = UserDatabase(callback.from_user.id)
    user.default = callback_data.value
    await callback.message.edit_text(f"Default изменён на {callback_data.value}")

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == 'default_group'))
async def default_group_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    user = UserDatabase(callback.from_user.id)
    user.default = callback_data.value

    await callback.message.edit_text(f"Default изменён на {callback_data.value}")
    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()
