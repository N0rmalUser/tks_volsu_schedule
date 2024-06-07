from aiogram import F, Router
from aiogram.types import FSInputFile, Message
from aiogram.filters import Command, CommandObject

from bot import database as db
from bot.filters import ChatTypeIdFilter
from bot.markups import admin_markups as kb
from bot.misc import user_activity

from config import ACTIVITIES_DB, ADMIN_CHAT_ID, LOG_FILE, SCHEDULE_DB, USERS_DB

import importlib

import logging

router = Router()


@router.message(Command("day_stat"), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def handle_send_daily_plot(msg: Message) -> None:
    """Отправляет график количества пользователей по дням."""
    db.update_user_activity_stats()
    user_activity.plot_user_activity_by_days()
    await msg.answer_photo(FSInputFile('data/user_activity_by_days.png'))


@router.message(Command("hour_stat"), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def handle_send_hourly_plot(msg: Message) -> None:
    """Отправляет график количества пользователей по часам для определённого дня."""
    db.update_user_activity_stats()
    user_activity.plot_user_activity_by_hours()
    await msg.answer_photo(FSInputFile('data/user_activity_by_hours.png'))


@router.message(Command("menu"), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def handle_topic_command_track(msg: Message) -> None:
    """Отправляет меню админа."""

    await msg.answer("Меню админа", reply_markup=kb.admin_menu)


@router.message(Command('ban'), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def ban_command_handler(msg: Message) -> None:
    """Банит пользователя. Изменяет значение столбца banned в базе данных."""

    user_id = db.get_user_id(msg.message_thread_id)
    db.set_banned(user_id, True)
    await msg.answer("Мы его забанили!!!")
    await getattr(importlib.import_module("bot.bot"), "send_custom_message")(user_id, "За нарушение правил, тебя забанили")
    logging.info(f'Забанен юзверь {user_id}')


@router.message(Command('unban'), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def ban_command_handler(msg: Message) -> None:
    """Разбанивает пользователя. Изменяет значение столбца banned в базе данных."""

    user_id = db.get_user_id(msg.message_thread_id)
    db.set_banned(user_id, False)
    await msg.answer("Мы его разбанили!!!")
    await getattr(importlib.import_module("bot.bot"), "send_custom_message")(user_id, "Амнистия! Тебя разбанили")
    logging.info(f'Разбанен юзверь {user_id}')


@router.message(Command("log"), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def log_handler(msg: Message, command: CommandObject) -> None:
    """Присылает логи бота в админский чат. Либо очищает их."""

    if command.args == 'send' or command.args == 'show':
        await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
    elif command.args == 'clear' or command.args == 'del':
        open(LOG_FILE, 'w').write('')
        await msg.answer("Логи очищены")
    else:
        await msg.answer("Такой команды нету (аргумент не правильный)")


@router.message(Command("send_db"), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def send_db_handler(msg: Message) -> None:
    """Отправляет базу данных пользователей в админский чат."""

    if msg.message_thread_id:
        await msg.answer_document(FSInputFile(USERS_DB), caption="Вот ваша база данных")


@router.message(Command("dump"), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def dump_handler(msg: Message) -> None:
    """Отправляет базу данных пользователей и логи в админский чат."""

    try:
        await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
        open(LOG_FILE, 'w').write('')
        logging.info("Отчищены логи")
    except Exception as e:
        logging.error('Ошибка при отчистке логов', e)
    try:
        await msg.answer_document(FSInputFile(USERS_DB), caption="Вот ваша база данных")
        logging.info("Выгружена база данных пользователей")
    except Exception as e:
        logging.error("Ошибка при выгрузке базы данных пользователей", e)
    try:
        await msg.answer_document(FSInputFile(ACTIVITIES_DB), caption="Вот ваша база данных")
        logging.info("Выгружена база данных активности")
    except Exception as e:
        logging.error("Ошибка при выгрузке базы данных активности", e)


@router.message(Command("track"), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def handle_topic_command_track(msg: Message, command: CommandObject) -> None:
    """Включает/выключает трекинг для пользователя или для всех пользователей."""

    if command.args is None:
        await msg.answer("Ошибка: не переданы аргументы")
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
            await resp.edit_text(f"Трекаются: \n" + tracked if users else "Никто не трекается", parse_mode='MarkdownV2')


@router.message(Command("info"), ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def handle_topic_command_info(msg: Message) -> None:
    """Присылает информацию о пользователе или о всех пользователях в зависимости от топика"""

    start = await msg.answer("Собираю статистику")
    if start.message_thread_id:
        await start.edit_text(db.get_user_info(db.get_user_id(msg.message_thread_id)), parse_mode="MarkdownV2")
    else:
        await start.edit_text(db.get_all_users_info())


@router.message(F.document, ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID))
async def file_handler(msg: Message):
    """Ловит документы и заменяет файл schedule.db, users.db, activities.db на полученные."""
    file_name = msg.document.file_name
    if file_name == "schedule.db":
        existing_file = SCHEDULE_DB.replace('/tks_schedule/', '')
        await getattr(importlib.import_module("bot.bot"), "get_file")(msg, existing_file)
        logging.info('Заменили расписание')
        await msg.answer('Заменили расписание')
    elif file_name == "users.db":
        existing_file = USERS_DB.replace('/tks_schedule/', '')
        await getattr(importlib.import_module("bot.bot"), "get_file")(msg, existing_file)
        logging.info('Заменили базу данных пользователей')
        await msg.answer('Заменили базу данных пользователей')
    elif file_name == "activities.db":
        existing_file = ACTIVITIES_DB.replace('/tks_schedule/', '')
        await getattr(importlib.import_module("bot.bot"), "get_file")(msg, existing_file)
        logging.info('Заменили базу данных активности пользователей')
        await msg.answer('Заменили базу данных активности пользователей')
    else:
        await msg.answer("Этот файл нельзя заменить")
        logging.info(f"{msg.from_user.id} пытался заменить файл {file_name}")
        await msg.forward(ADMIN_CHAT_ID)


@router.message(ChatTypeIdFilter(chat_type=['group', 'supergroup'], chat_id=ADMIN_CHAT_ID))
async def handle_topic_message(msg: Message) -> None:
    """Отправляет сообщение в личный топик пользователя"""

    try:
        if '/' in msg.text[0]:
            await msg.answer("Нет такой команды, но я тебя спас, не бойся")
        else:
            if msg.message_thread_id is not None:
                await getattr(importlib.import_module("bot.bot"), "send_to_user")(msg)
            else:
                await getattr(importlib.import_module("bot.bot"), "broadcast")(msg)
    except TypeError:
        pass
