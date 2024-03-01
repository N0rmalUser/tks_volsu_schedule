from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot import database as db
from bot.markups import user_markups as kb
from bot.markups.keyboard_factory import ChangeCallbackFactory, DayCallbackFactory
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
    keyboard_type: str = callback_data.keyboard_type
    value: str = callback_data.value
    week: int = callback_data.week
    day: int = callback_data.day

    user_id = int(callback.from_user.id)

    if callback_data.day == db.get_day(user_id):
        await callback.answer()
        return
    db.set_day(user_id, callback_data.day)

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(day=day, week=week, teacher_name=value)
        week_kb = kb.get_days(user_id=user_id, keyboard_type='teacher', week=week, value=value)
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(day=day, week=week, group_name=value)
        week_kb = kb.get_days(user_id=user_id, keyboard_type='group', week=week, value=value)
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(day=day, week=week, room_name=value)
        week_kb = kb.get_days(user_id=user_id, keyboard_type='room', week=week, value=value)
    else:
        logging.error(f"{user_id} сделал неизвестный callback (teacher, group, room): {callback.data} в _week_day_handler")
        await callback.answer("Неизвестный тип запроса. Напишите админу /admin")
        return

    await callback.message.edit_text(text, reply_markup=week_kb)

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(DayCallbackFactory.filter(F.action == "week"))
async def week_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    keyboard_type = callback_data.keyboard_type
    value = callback_data.value
    week = 1 if int(callback_data.week) != 2 else 2
    day = callback_data.day

    user_id = int(callback.from_user.id)

    if callback_data.day == str(db.get_day(user_id)):
        await callback.answer()
        return
    db.set_day(user_id, callback_data.day)

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(day=day, week=week, teacher_name=value)
        week_kb = kb.get_days(user_id, keyboard_type='teacher', week=week, value=value)
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(day=day, week=week, group_name=value)
        week_kb = kb.get_days(user_id, keyboard_type='group', week=week, value=value)
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(day=day, week=week, room_name=value)
        week_kb = kb.get_days(user_id, keyboard_type='room', week=week, value=value)
    else:
        logging.error(f"{user_id} сделал неизвестный callback (teacher, group, room): {callback.data} в _week_day_handler")
        await callback.answer("Неизвестный тип запроса. Напишите админу /admin")
        return

    await callback.message.edit_text(text, reply_markup=week_kb)

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "room"))
async def room_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    user_id = int(callback.from_user.id)

    db.set_today_date(user_id)
    db.set_room(user_id, callback_data.value)

    await callback.message.edit_text(text_maker.get_room_schedule(day=db.get_day(user_id), week=db.get_week(user_id), room_name=callback_data.value),
                                     reply_markup=kb.get_days(user_id, keyboard_type='room', week=db.get_week(user_id), value=callback_data.value))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == 'teacher'))
async def teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    user_id = int(callback.from_user.id)

    db.set_today_date(user_id)
    db.set_teacher(user_id, callback_data.value)

    await callback.message.edit_text(text_maker.get_teacher_schedule(day=db.get_day(user_id), week=db.get_week(user_id), teacher_name=callback_data.value),
                                     reply_markup=kb.get_days(user_id, keyboard_type='teacher', week=db.get_week(user_id), value=callback_data.value))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == 'group'))
async def teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    user_id = int(callback.from_user.id)

    db.set_today_date(user_id)
    db.set_group(user_id, callback_data.value)

    await callback.message.edit_text(text_maker.get_group_schedule(day=db.get_day(user_id), week=db.get_week(user_id), group_name=callback_data.value),
                                     reply_markup=kb.get_days(user_id, keyboard_type='group', week=db.get_week(user_id), value=callback_data.value))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()
