from aiogram import Router
from aiogram.types import Message, FSInputFile, Document
from aiogram.filters import Command, CommandObject

from bot import database as db
from bot.filters import ChatTypeFilter

from config import ADMIN_CHAT_ID, LOG_FILE, USERS_DB

from bot.markups import admin_markups as kb

import importlib

import logging

router = Router()


@router.message(Command("menu"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def handle_topic_command_track(msg: Message) -> None:
    """Отправляет меню админа."""
    if msg.chat.id == ADMIN_CHAT_ID:
        await msg.answer("Меню админа", reply_markup=kb.admin_menu)


@router.message(Command('ban'), ChatTypeFilter(chat_type=['group', 'supergroup']))
async def ban_command_handler(msg: Message) -> None:
    """Банит пользователя. Изменяет значение столбца banned в базе данных."""
    if msg.chat.id == ADMIN_CHAT_ID:
        user_id = db.get_user_id(msg.message_thread_id)
        db.set_banned(user_id, True)
        await msg.answer("Мы его забанили!!!")
        await getattr(importlib.import_module("bot.bot"), "send_custom_message")(user_id, "За нарушение правил, тебя забанили")
        logging.info(f'Забанен юзверь {user_id}')


@router.message(Command('unban'), ChatTypeFilter(chat_type=['group', 'supergroup']))
async def ban_command_handler(msg: Message) -> None:
    """Разбанивает пользователя. Изменяет значение столбца banned в базе данных."""
    if msg.chat.id == ADMIN_CHAT_ID:
        user_id = db.get_user_id(msg.message_thread_id)
        db.set_banned(user_id, False)
        await msg.answer("Мы его разбанили!!!")
        await getattr(importlib.import_module("bot.bot"), "send_custom_message")(user_id, "Амнистия! Тебя разбанили")
        logging.info(f'Разбанен юзверь {user_id}')


@router.message(Command("log"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def log_handler(msg: Message, command: CommandObject) -> None:
    """Присылает логи бота в админский чат. Либо очищает их."""
    print(command)
    if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
        if command.args == 'send' or command.args == 'show':
            await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
        elif command.args == 'clear' or command.args == 'del':
            open(LOG_FILE, 'w').write('')
            await msg.answer("Логи очищены")
        else:
            await msg.answer("Такой команды нету (аргумент не правильный)")


@router.message(Command("send_db"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def send_db_handler(msg: Message) -> None:
    """Отправляет базу данных пользователей в админский чат."""
    if msg.chat.id == ADMIN_CHAT_ID:
        if msg.message_thread_id:
            await msg.answer_document(FSInputFile(USERS_DB), caption="Вот ваша база данных")


@router.message(Command("dump"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def dump_handler(msg: Message) -> None:
    """Отправляет базу данных пользователей и логи в админский чат."""
    if msg.chat.id == ADMIN_CHAT_ID:
        try:
            await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
            open(LOG_FILE, 'w').write('')
            await msg.answer_document(FSInputFile(USERS_DB), caption="Вот ваша база данных")
            logging.info("Выгружены базы данных и логов")
        except Exception:
            logging.error("Ошибка при выгрузке базы данных и логов")


@router.message(Command("send_schedule"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def schedule_update_handler(msg: Message) -> None:
    """Отправляет файл с расписанием для обновления последующего."""
    await msg.answer_document('data/schedule.db', caption='Отправьте исправленную бд для обновления расписания')


@router.message(Command("track"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def handle_topic_command_track(msg: Message, command: CommandObject) -> None:
    """Включает/выключает трекинг для пользователя или для всех пользователей."""
    if msg.chat.id == ADMIN_CHAT_ID:
        if command.args is None:
            await msg.answer(
                "Ошибка: не переданы аргументы"
            )
            return
        command = str(command.args).lower()
        resp = await msg.answer("Подождите...")
        if resp.message_thread_id:
            user_id = db.get_user_id(resp.message_thread_id)
            if command == "start":
                db.set_tracking(user_id, True)
            elif command == "stop":
                db.set_tracking(user_id, False)
            elif command == "status":
                pass
            await resp.edit_text(f"Трекинг {'включен' if db.get_tracking(user_id) else 'выключен'}")
        else:
            if command == "start":
                await db.tracking_manage(True)
                await resp.edit_text("Трекинг включен для всех пользователей")
            elif command == "stop":
                await db.tracking_manage(False)
                await resp.edit_text("Трекинг выключен для всех пользователей")
            elif command == "status":
                users = await db.get_tracked_users()
                tracked = '\n'.join([str(user) for user in users])
                await resp.edit_text(f"Трекаются: \n" + tracked if users else "Никто не трекается",
                                     parse_mode='MarkdownV2')


@router.message(Command("info"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def handle_topic_command_info(msg: Message) -> None:
    """Присылает информацию о пользователе или о всех пользователях в зависимости от топика"""
    if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
        start = await msg.answer("Собираю статистику")
        if start.message_thread_id:
            await start.edit_text(db.get_user_info(db.get_user_id(msg.message_thread_id)),
                                  parse_mode="MarkdownV2")
        else:
            await start.edit_text(db.get_all_users_info())


@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def handle_topic_message(msg: Message) -> None:
    """Отправляет сообщение в личный топик пользователя"""
    try:
        if msg.text[0] != '/':
            if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
                if msg.message_thread_id is not None:
                    await getattr(importlib.import_module("bot.bot"), "send_to_user")(msg)
                else:
                    await getattr(importlib.import_module("bot.bot"), "broadcast")(msg)
        else:
            await msg.answer("Нет такой команды, но я тебя спас, не бойся")
    except TypeError:
        pass


@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def schedule_handler(msg: Document):
    """Ловит документы и заменяет файл schedule.db на полученный"""
    if msg.chat.id == ADMIN_CHAT_ID:
        await getattr(importlib.import_module("bot.bot"), "get_file")(msg)
