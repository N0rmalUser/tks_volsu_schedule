from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot import database as db
from bot.markups import user_markups as kb
from bot.markups.keyboard_factory import ChangeCallbackFactory, DayCallbackFactory
from bot.misc import text_maker

import importlib

import logging

router = Router()


@router.callback_query(lambda c: c.data.startswith("ignore"))
async def _ignore_handler(callback: CallbackQuery) -> None:
    """Функция, сбрасывающая нажатия кнопки без функционала."""
    await callback.answer("Сейчас эта неделя")


@router.callback_query(DayCallbackFactory.filter(F.action == "day"))
async def day_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    callback_type = callback_data.call_type
    user_id = int(callback.from_user.id)

    if callback_data.value == str(db.get_day(user_id)):
        await callback.answer()
        return
    db.set_day(user_id, callback_data.value)

    if callback_type == "teacher":
        text = text_maker.get_teacher_schedule(user_id)
        week_kb = kb.get_days(type='teacher', week=db.get_week(user_id))
    elif callback_type == "group":
        text = text_maker.get_group_schedule(user_id)
        week_kb = kb.get_days(type='group', week=db.get_week(user_id))
    elif callback_type == "room":
        text = text_maker.get_room_schedule(user_id)
        week_kb = kb.get_days(type='room', week=db.get_week(user_id))
    else:
        logging.error(f"{user_id} сделал неизвестный callback (teacher, group, room): {callback.data} в _week_day_handler")
        await callback.answer("Неизвестный тип запроса. Напишите админу /admin")
        return

    await callback.message.edit_text(text, reply_markup=week_kb)

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(DayCallbackFactory.filter(F.action == "week"))
async def week_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    callback_type = callback_data.call_type
    user_id = int(callback.from_user.id)

    if callback_data.value == str(db.get_day(user_id)):
        await callback.answer()
        return
    db.set_week(user_id, callback_data.value)

    if callback_type == "teacher":
        text = text_maker.get_teacher_schedule(user_id)
        week_kb = kb.get_days(type='teacher', week=db.get_week(user_id))
    elif callback_type == "group":
        text = text_maker.get_group_schedule(user_id)
        week_kb = kb.get_days(type='group', week=db.get_week(user_id))
    elif callback_type == "room":
        text = text_maker.get_room_schedule(user_id)
        week_kb = kb.get_days(type='room', week=db.get_week(user_id))
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

    await callback.message.edit_text(text_maker.get_teacher_schedule(user_id),
                                     reply_markup=kb.get_days(type='room', week=db.get_week(user_id)))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == 'teacher'))
async def teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    user_id = int(callback.from_user.id)
    db.set_today_date(user_id)

    db.set_teacher(user_id, callback_data.value)

    await callback.message.edit_text(text_maker.get_teacher_schedule(user_id),
                                     reply_markup=kb.get_days(type='teacher', week=db.get_week(user_id)))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == 'group'))
async def teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    user_id = int(callback.from_user.id)
    db.set_today_date(user_id)

    db.set_group(user_id, callback_data.value)

    await callback.message.edit_text(text_maker.get_teacher_schedule(user_id),
                                     reply_markup=kb.get_days(type='group', week=db.get_week(user_id)))

    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()
