from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandObject

import asyncio

from bot import database as db
from bot.filters import ChatTypeFilter

from config import ADMIN_CHAT_ID, LOG_FILE, DB_PATH

from bot.markups import admin_markups as kb

import importlib

router = Router()


@router.message(Command("menu"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_track(msg: Message) -> None:
    if msg.chat.id == ADMIN_CHAT_ID:
        await msg.answer("Меню админа", reply_markup=kb.admin_menu)


@router.message(Command("log"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_track(msg: Message, command: CommandObject) -> None:
    if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
        if command.args == 'send' or command.args == 'show':
            await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
        elif command.args == 'clear' or command.args == 'del':
            open(LOG_FILE, 'w').write('')
            await msg.answer("Логи очищены")
        else:
            await msg.answer("Такой команды нету (аргумент не правильный)")


@router.message(Command("send_db"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_track(msg: Message) -> None:
    if msg.chat.id == ADMIN_CHAT_ID:
        if msg.message_thread_id:
            await msg.answer_document(FSInputFile(DB_PATH), caption="Вот ваша база данных")


@router.message(Command("schedule_update"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _schedule_update_handler(msg: Message) -> None:
    """/schedule_update command handler. Update schedule json file."""
    wait_msg = await msg.answer("Сейчас обновиться, подождите")
    await asyncio.sleep(1)
    db.open_schedule_file()
    await wait_msg.delete()
    await msg.answer("Ура! Обновили schedules")


@router.message(Command("track"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_track(msg: Message, command: CommandObject) -> None:
    """/track [start,stop,status] command handler. Set tracking for user topic."""
    if msg.chat.id == ADMIN_CHAT_ID:
        if command.args is None:
            await msg.answer(
                "Ошибка: не переданы аргументы"
            )
            return
        command = str(command.args).lower()
        if msg.message_thread_id:
            user_id = db.get_user_id(msg.message_thread_id)
            if command == "start":
                db.set_tracking(user_id, True)
            elif command == "stop":
                db.set_tracking(user_id, False)
            elif command == "status":
                pass
            await msg.answer(f"Трекинг {'включен' if db.get_tracking(user_id) else 'выключен'}")
        else:
            if command == "start":
                await db.tracking_manage(True)
            elif command == "stop":
                await db.tracking_manage(False)
            elif command == "status":
                users = await db.get_tracked_users()
                tracked = '\n'.join([str(user) for user in users])
                await msg.answer(f"Трекаются: \n" + tracked if users else "Никто не трекается",
                                 parse_mode='MarkdownV2')


@router.message(Command("info"), ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_command_info(msg: Message) -> None:
    if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
        if msg.message_thread_id:
            await msg.answer(db.get_user_info(db.get_user_id(msg.message_thread_id)),
                             parse_mode="MarkdownV2")
        else:
            await msg.answer(db.get_all_users_info())


@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def _handle_topic_message(msg: Message) -> None:
    if msg.text[0] != '/':
        if msg.chat.id == ADMIN_CHAT_ID and not msg.from_user.is_bot:
            if msg.message_thread_id is not None:
                await getattr(importlib.import_module("bot.bot"), "send_to_user")(msg)
            else:
                await getattr(importlib.import_module("bot.bot"), "broadcast")(msg)
    else:
        await msg.answer("Нет такой команды, но я тебя спас, не бойся")
