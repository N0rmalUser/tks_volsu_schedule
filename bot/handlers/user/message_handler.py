from aiogram import Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload

from bot import database as db
from bot.filters import ChatTypeFilter
from bot.misc import text_maker
from bot.markups import user_markups as kb

from config import ADMIN_CHAT_ID

import importlib

router = Router()


@router.message(CommandStart(deep_link=True))
async def _start_deep_handler(msg: Message, command: CommandObject) -> None:
    try:
        payload = decode_payload(command.args)
        args = payload.split("=")
        user_id = int(msg.from_user.id)
        db.set_inviter(user_id, int(args[0]))
        if args[1] == "teacher":
            user_type = "teacher"
            menu, keyboard = kb.teacher_menu, kb.teachers
        else:
            user_type = "student"
            menu, keyboard = kb.student_menu, kb.groups
        db.set_last_date(msg)
        db.set_today_date(user_id)
        db.set_week(user_id, 1)
        db.set_user_type(msg, user_type)

        main = importlib.import_module("bot.bot")
        another_function = getattr(main, "start_message")
        await another_function(msg, user_id, menu, keyboard)
    except Exception:
        await msg.answer("Неверная ссылка")


@router.message(CommandStart())
async def _start_handler(msg: Message) -> None:
    user_id = int(msg.from_user.id)
    db.set_last_date(msg)
    db.set_today_date(user_id)
    db.set_week(user_id, 1)
    user_type = db.get_user_type(user_id)
    db.set_user_type(msg, user_type)
    menu, keyboard = (kb.teacher_menu, kb.teachers) if user_type == "teacher" else (
        kb.student_menu, kb.groups)
    await getattr(importlib.import_module("bot.bot"), "start_message")(msg, user_id, menu, keyboard)


@router.message(Command("admin"), ChatTypeFilter(chat_type="private"))
async def _admin_handler(msg: Message) -> None:
    await msg.answer("Модератор скоро напишет вам, ожидайте")
    await getattr(importlib.import_module("bot.bot"), "admin_sender")(msg)
    await msg.forward(ADMIN_CHAT_ID, from_chat_id=msg.chat.id, message_id=msg.message_id,
                      message_thread_id=db.get_topic_id(msg.from_user.id))
    db.set_tracking(db.get_user_id(msg.message_thread_id), True)


@router.message(ChatTypeFilter(chat_type="private"))
async def _handler(msg: Message) -> None:
    user_id = msg.from_user.id
    user_type = db.get_user_type(user_id)
    if msg.content_type == "text":
        if msg.text == "Расписание на сегодня":
            db.set_today_date(user_id)
            entity_id = db.get_teacher(user_id) if user_type == "teacher" else db.get_group(user_id)

            if not entity_id:
                await msg.answer(
                    f"Сначала выберите {'ФИО преподавателя' if user_type == 'teacher' else 'группу'}, нажав на соответствующую кнопку.")
                return
            if user_type == "teacher":
                week_kb = kb.teacher_week1 if db.get_week(user_id) == 1 else kb.teacher_week2
                await msg.answer(text_maker.get_teacher_schedule(user_id), reply_markup=week_kb)
            elif user_type == "student":
                week_kb = kb.group_week1 if db.get_week(user_id) == 1 else kb.group_week2
                await msg.answer(text_maker.get_group_schedule(user_id), reply_markup=week_kb)
            else:
                await msg.answer("Ошибка! Напишите админу /admin")
        elif msg.text == "Кабинеты":
            await msg.answer(f"Выберите кабинет", reply_markup=kb.rooms)
        elif msg.text == "Группы":
            await msg.answer(f"Выберите группу", reply_markup=kb.groups)
        elif msg.text == "Преподаватели":
            await msg.answer(f"Выберите преподавателя", reply_markup=kb.teachers)
        if db.get_tracking(user_id):
            await msg.forward(ADMIN_CHAT_ID, from_chat_id=msg.chat.id, message_id=msg.message_id,
                              message_thread_id=db.get_topic_id(msg.from_user.id))
    else:
        await msg.answer("Я тебя не понимаю, буковы пиши!")
    db.set_last_date(msg)
