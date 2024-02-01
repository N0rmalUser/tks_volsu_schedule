from aiogram import Router

from bot import database as db
from bot.misc import text_maker
from bot.markups import user_markups as kb

from aiogram.types import CallbackQuery

import importlib

router = Router()


@router.callback_query(lambda c: c.data.startswith("ignore"))
async def _ignore_handler(callback: CallbackQuery) -> None:
    """Функция, сбрасывающая нажатия кнопки без функционала."""
    await callback.answer("Сейчас эта неделя")


@router.callback_query(lambda c: c.data.startswith("week-") or c.data.startswith("day/"))
async def _week_day_handler(callback: CallbackQuery) -> None:
    """Ловит коллбеки с неделями и днями. И отсылает юзеру расписание на эту неделю и день."""
    data = callback.data
    user_id = int(callback.from_user.id)
    if data.startswith("week-"):
        _, callback_type, week = data.split('-')
        day = db.get_day(user_id)
        db.set_week(user_id, week)
    elif data.startswith("day/"):
        _, callback_type, week, day = data.split('/')
        if day == db.get_day(user_id):
            await callback.answer()
            return
    else:
        await callback.answer("Неизвестный тип запроса.")
        return
    db.set_day(user_id, day)
    db.set_week(user_id, week)

    if callback_type == "teacher":
        text = text_maker.get_teacher_schedule(user_id)
        kb1, kb2 = kb.teacher_week1, kb.teacher_week2
    elif callback_type == "group":
        text = text_maker.get_group_schedule(user_id)
        kb1, kb2 = kb.group_week1, kb.group_week2
    elif callback_type == "room":
        text = text_maker.get_room_schedule(user_id)
        kb1, kb2 = kb.room_week1, kb.room_week2
    else:
        await callback.answer("Неизвестный тип запроса.")
        return

    if db.get_week(user_id) == 1:
        await callback.message.edit_text(text, reply_markup=kb1)
    elif db.get_week(user_id) == 2:
        await callback.message.edit_text(text, reply_markup=kb2)
    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("room-") or c.data.startswith("teacher-") or c.data.startswith("group-"))
async def _room_teacher_group_handler(callback: CallbackQuery) -> None:
    """Ловит коллбеки с аудиториями, преподавателями и группами. И отсылает юзеру расписание этого препода, группы или аудитории."""
    user_id = int(callback.from_user.id)
    db.set_today_date(user_id)
    data_parts = callback.data.split('-')
    callback_type = data_parts[0]
    entity_id = "-".join(data_parts[1:])
    if callback_type == "room":
        db.set_room(user_id, entity_id)
        text = text_maker.get_room_schedule(user_id)
        week_kb1, week_kb2 = kb.room_week1, kb.room_week2
    elif callback_type == "teacher":
        db.set_teacher(user_id, entity_id)
        text = text_maker.get_teacher_schedule(user_id)
        week_kb1, week_kb2 = kb.teacher_week1, kb.teacher_week2
    elif callback_type == "group":
        db.set_group(user_id, entity_id)
        text = text_maker.get_group_schedule(user_id)
        week_kb1, week_kb2 = kb.group_week1, kb.group_week2
    else:
        await callback.answer("Неизвестный тип запроса.")
        return

    if db.get_week(user_id) == 1:
        await callback.message.edit_text(text, reply_markup=week_kb1)
    elif db.get_week(user_id) == 2:
        await callback.message.edit_text(text, reply_markup=week_kb2)
    await getattr(importlib.import_module("bot.bot"), "send_callback")(callback)
    await callback.answer()
