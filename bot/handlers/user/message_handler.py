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

import logging

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_deep_handler(msg: Message, command: CommandObject) -> None:
    """Обработчик команды /start с deep_link'ом. Назначает тип пользователя в зависимости от ссылки, а также добавляет id пригласившего пользователя в базу данных."""
    try:
        payload = decode_payload(command.args)
        args = payload.split("=")
        user_id = int(msg.from_user.id)
        db.set_inviter(user_id, int(args[0]))
        if args[1] == "teacher":
            user_type = "teacher"
            menu, keyboard = kb.teacher_menu, kb.get_teachers()
        else:
            user_type = "student"
            menu, keyboard = kb.student_menu, kb.get_groups()
        db.set_last_date(msg)
        db.set_today_date(user_id)
        db.set_week(user_id, 1)
        db.set_user_type(msg, user_type)

        await getattr(importlib.import_module("bot.bot"), "start_message")(msg, user_id, menu, keyboard)
    except Exception:
        logging.warning(f"{msg.from_user.id} перешёл по неверной ссылке")
        await msg.answer("Неверная ссылка")


@router.message(CommandStart())
async def start_handler(msg: Message) -> None:
    """Обработчик команды /start без deep_link'а."""
    user_id = int(msg.from_user.id)
    db.set_last_date(msg)
    db.set_today_date(user_id)
    db.set_week(user_id, 1)
    user_type = db.get_user_type(user_id)
    db.set_user_type(msg, user_type)
    menu, keyboard = (kb.teacher_menu, kb.get_teachers()) if user_type == "teacher" else (kb.student_menu, kb.get_groups())
    await getattr(importlib.import_module("bot.bot"), "start_message")(msg, user_id, menu, keyboard)


@router.message(Command('help'), ChatTypeFilter(chat_type='private'))
async def help_handler(msg: Message) -> None:
    """Обработчик команды /help. Отправляет сообщение с описанием бота."""
    if db.get_user_type == 'teacher':
        await msg.answer("""
Привет, это бот расписания кафедры ТКС!

Кнопка `Расписание на сегодня` показываает расписание на сегодняшний день для выбранного преподавателя.
Кнопки `Группы`, `Преподаватели`, `Кабинеты` открывают соответствующие меню выбора.

Если у группы номер `ИБТС-231_2` - это 2-я подгруппа, если `_2` отсутствует, то должно придти вся группа, либо первая подгруппа. Отдельно первая подгруппа ни как не обозначается!!!

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️

Для связи с администратором при возникших ошибках/измнениях в расписании используйте команду /admin и опишите проблему.
""")
    else:
        await msg.answer("""
Привет, это бот расписания кафедры ТКС!

Кнопка `Расписание на сегодня` показываает расписание на сегодняшний день для выбранной группы.
Кнопка `Группы` открывает меню выбора групп

Если у группы номер `ИБТС-231_2` - это 2-я подгруппа, если `_2` отсутствует, первая

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️

Для связи с администратором при возникших ошибках/измнениях в расписании используйте команду /admin и опишите проблему.
""")


@router.message(Command("admin"), ChatTypeFilter(chat_type="private"))
async def admin_handler(msg: Message) -> None:
    """Обработчик команды /admin. Пересылает сообщение админу и включает слежку за действиями пользователя."""
    await getattr(importlib.import_module("bot.bot"), "admin_sender")(msg)
    await msg.forward(chat_id=ADMIN_CHAT_ID, message_thread_id=db.get_topic_id(msg.from_user.id))
    await msg.answer("Модератор скоро напишет вам, ожидайте")
    db.set_tracking(msg.from_user.id, True)
    logging.info(f"{msg.from_user.id} написал админу")


@router.message(ChatTypeFilter(chat_type="private"))
async def handler(msg: Message) -> None:
    """Обработчик сообщений от пользователя. Отправляет расписание на сегодня, если пользователь выбрал преподавателя, группу или кабинет."""
    user_id = msg.from_user.id
    user_type = db.get_user_type(user_id)
    if msg.content_type == "text":
        if msg.text == "Расписание на сегодня":
            db.set_today_date(user_id)
            entity_id = db.get_teacher(user_id) if user_type == "teacher" else db.get_group(user_id)

            if not entity_id:
                await msg.answer(f"Сначала выберите {'ФИО преподавателя' if user_type == 'teacher' else 'группу'}, нажав на соответствующую кнопку.")
                return
            if user_type == "teacher":
                week_kb = kb.get_days(user_id, 'teacher', db.get_week(user_id), value=entity_id)
                await msg.answer(text_maker.get_teacher_schedule(day=db.get_day(user_id), week=db.get_week(user_id), teacher_name=entity_id), reply_markup=week_kb)
            elif user_type == "student":
                week_kb = kb.get_days(user_id, 'group', db.get_week(user_id), value=entity_id)
                await msg.answer(text_maker.get_group_schedule(day=db.get_day(user_id), week=db.get_week(user_id), group_name=entity_id), reply_markup=week_kb)
            else:
                logging.info(f"{msg.from_user.id} неправильный тип пользователя")
                await msg.answer("Ошибка! Напишите админу /admin")
        elif msg.text == "Кабинеты":
            await msg.answer(f"Выберите кабинет", reply_markup=kb.get_rooms())
        elif msg.text == "Группы":
            await msg.answer(f"Выберите группу", reply_markup=kb.get_groups())
        elif msg.text == "Преподаватели":
            await msg.answer(f"Выберите преподавателя", reply_markup=kb.get_teachers())
        else:
            logging.info(f"{msg.from_user.id} написал неправильную команду")
            if not db.get_tracking(user_id):
                await msg.answer("Я не знаю такой команды")
        if db.get_tracking(user_id):
            await msg.forward(ADMIN_CHAT_ID, message_thread_id=db.get_topic_id(msg.from_user.id))
    else:
        await msg.answer("Я тебя не понимаю, буковы пиши!")
    db.set_last_date(msg)
