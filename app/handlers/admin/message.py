# TKS VOLSU SCHEDULE BOT
# Copyright (C) 2024 N0rmalUser
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from app.config import (
    ACTIVITIES_DB,
    ADMIN_CHAT_ID,
    ADMIN_ID,
    COLLEGE_SHEETS_PATH,
    COLLEGE_TEACHERS,
    GROUPS_SCHEDULE_PATH,
    LOG_FILE,
    PLOT_PATH,
    SCHEDULE_DB,
    USERS_DB,
)
from app.database import get_all_users_info, get_tracked_users, tracking_manage, user_info
from app.database.user import UserDatabase
from app.filters import ChatTypeIdFilter
from app.markups import admin_markups as kb

router = Router()


@router.message(
    Command("month"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_send_daily_plot(msg: Message, command: CommandObject = None) -> None:
    """Отправляет график количества пользователей по дням."""

    from datetime import datetime

    from app.database import activity as db
    from app.misc import user_activity

    month = (
        datetime.strptime(command.args, "%d.%m.%Y") if command.args else datetime.now()
    ).strftime("%Y-%m-%d")
    if msg.message_thread_id and msg.message_thread_id != 1:  # TODO: Починить топики
        activity = db.get_user_activity_for_month(
            user_id=UserDatabase(topic_id=msg.message_thread_id).tg_id(),
            date_str=month,
        )
    else:
        activity = db.get_activity_for_month(date_str=month)
    user_activity.plot_activity_for_month(
        activity, datetime.strptime(month, "%Y-%m-%d").strftime("%d %B %Y")
    )
    await msg.answer_document(FSInputFile(PLOT_PATH / "activity_for_month.html"))


@router.message(
    Command("day"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_send_hourly_plot(msg: Message, command: CommandObject = None) -> None:
    """Отправляет график количества пользователей по часам для определённого дня."""

    from datetime import datetime

    from app.database import activity as db
    from app.misc import user_activity

    date = (
        datetime.strptime(command.args, "%d.%m.%Y") if command.args else datetime.now()
    ).strftime("%Y-%m-%d")
    if msg.message_thread_id:
        activity = db.get_user_activity_for_day(
            user_id=UserDatabase(topic_id=msg.message_thread_id).tg_id(), date_str=date
        )
    else:
        activity = db.get_activity_for_day(date_str=date)
    user_activity.plot_activity_for_day(
        activity, datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y")
    )
    await msg.answer_document(FSInputFile(PLOT_PATH / "activity_for_day.html"))


@router.message(
    Command("menu"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_track(msg: Message) -> None:
    await msg.answer("Меню админа", reply_markup=kb.admin_menu())


@router.message(
    Command("ban"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def ban_command_handler(msg: Message) -> None:
    """Банит пользователя. Изменяет значение столбца banned в базе данных."""
    user = UserDatabase(topic_id=msg.message_thread_id)
    user.banned = True
    await msg.answer("Мы его забанили!!!")
    await msg.bot.send_message(user.tg_id(), "За нарушение правил, тебя забанили")
    logging.info(f"Забанен юзверь {user.tg_id()}")


@router.message(
    Command("unban"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def ban_command_handler(msg: Message) -> None:
    """Разбанивает пользователя. Изменяет значение столбца banned в базе данных."""

    user = UserDatabase(topic_id=msg.message_thread_id)
    user.banned = False
    await msg.answer("Мы его разбанили!!!")
    await msg.bot.send_message(user.tg_id(), "Амнистия! Тебя разбанили")
    logging.info(f"Разбанен юзверь {user.tg_id()}")


@router.message(
    Command("dump"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def dump_handler(msg: Message) -> None:
    """Отправляет базу данных пользователей и логи в админский чат."""

    try:
        await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
        open(LOG_FILE, "w").write("")
        logging.info("Выгружены и отчищены логи")
    except Exception as e:
        logging.error("Ошибка при отчистке логов", e)
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
    try:
        await msg.answer_document(FSInputFile(SCHEDULE_DB), caption="Вот ваше расписание")
        logging.info("Выгружено расписание")
    except Exception as e:
        logging.error("Ошибка при выгрузке расписания", e)


@router.message(
    Command("log"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def dump_handler(msg: Message) -> None:
    """Отправляет базу данных пользователей и логи в админский чат."""

    try:
        await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
        open(LOG_FILE, "w").write("")
        logging.info("Выгружены и отчищены логи")
    except Exception as e:
        logging.error("Ошибка при отчистке логов", e)


@router.message(
    Command("college"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def college_handler(msg: Message) -> None:
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            for teacher in COLLEGE_TEACHERS.values():
                await session.post(
                    url="https://app.volsu.ru/api/bot/select-teacher",
                    json={"teacherId": teacher, "telegramId": ADMIN_ID, "start": "download"},
                )
        logging.info("Расписание преподавателей колледжа успешно скачано")
    except Exception as e:
        await msg.answer("Ошибка вытаскивания расписания из колледжского бота")
        logging.error(e)


@router.message(
    Command("update"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def update_handler(msg: Message) -> None:
    from app.misc import schedule_parser

    start = await msg.answer("Подождите...")
    try:
        schedule_parser.college_schedule_parser()
        schedule_parser.university_schedule_parser()
        await start.edit_text("База данных расписания обновлена")
        logging.info("База данных расписания обновлена")
    except Exception as e:
        await start.edit_text("Ошибка обновления базы данных расписания")
        logging.error(e)


@router.message(
    Command("track"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_track(msg: Message, command: CommandObject) -> None:
    """Включает/выключает трекинг для пользователя или для всех пользователей."""

    if command.args is None:
        await msg.answer("Ошибка: не переданы аргументы")
        return

    command = str(command.args).lower()
    start = await msg.answer("Подождите...")

    if start.message_thread_id:
        user = UserDatabase(topic_id=msg.message_thread_id)
        if command == "start":
            user.tracking = True
        elif command == "stop":
            user.tracking = False
        elif command == "status":
            pass
        await start.edit_text(f"Трекинг {'включен' if user.tracking else 'выключен'}")
    else:
        if command == "start":
            await tracking_manage(True)
            await start.edit_text("Трекинг включен для всех пользователей")
        elif command == "stop":
            await tracking_manage(False)
            await start.edit_text("Трекинг выключен для всех пользователей")
        elif command == "status":
            users = await get_tracked_users()
            tracked = "\n".join([str(user) for user in users])
            await start.edit_text(
                f"Трекаются: \n" + tracked if users else "Никто не трекается",
                parse_mode="MarkdownV2",
            )


@router.message(
    Command("info"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_info(msg: Message, command: CommandObject = None) -> None:
    """Присылает информацию о пользователе или о всех пользователях в зависимости от топика"""

    start = await msg.answer(text="Собираю статистику")
    if command.args is None:
        if start.message_thread_id:
            await start.edit_text(
                text=user_info(UserDatabase(topic_id=msg.message_thread_id).tg_id()),
                parse_mode="HTML",
            )
        else:
            await start.edit_text(text=get_all_users_info())
    else:
        await start.edit_text(user_info(int(command.args)), parse_mode="MarkdownV2")


@router.message(
    Command("teacher"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_teacher(msg: Message) -> None:
    start = await msg.answer("Изменяю тип пользователя...")
    if start.message_thread_id:
        user = UserDatabase(topic_id=msg.message_thread_id)
        user.type = "teacher"
        await start.edit_text("Тип пользователя изменён на `teacher`")


@router.message(
    Command("student"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_student(msg: Message) -> None:
    start = await msg.answer("Изменяю тип пользователя...")
    if start.message_thread_id:
        user = UserDatabase(topic_id=msg.message_thread_id)
        user.type = "student"
        await start.edit_text("Тип пользователя изменён на `student`")


@router.message(
    F.document,
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def file_handler(msg: Message):
    """Ловит документы и заменяет файл schedule.db, users.db, activities.db на полученные."""

    file_name = msg.document.file_name
    file_map = {
        "schedule.db": {
            "path": SCHEDULE_DB,
            "message": "Заменили расписание",
        },
        "users.db": {
            "path": USERS_DB,
            "message": "Заменили базу данных пользователей",
        },
        "activities.db": {
            "path": ACTIVITIES_DB,
            "message": "Заменили базу данных активности пользователей",
        },
        ".xlsx": {
            "path": COLLEGE_SHEETS_PATH,
            "message": f"Заменил файл {file_name}",
        },
        ".docx": {
            "path": GROUPS_SCHEDULE_PATH,
            "message": f"Заменил файл {file_name}",
        },
    }

    key = next((key for key in file_map if key in file_name), None)

    if key:
        file_id = msg.document.file_id
        file_info = await msg.bot.get_file(file_id)
        downloaded_file = await msg.bot.download_file(file_info.file_path)

        with open(file_map[key]["path"] / file_name, "wb") as new_file:
            new_file.write(downloaded_file.read())

        logging.info(file_map[key]["message"])
        await msg.answer(file_map[key]["message"])
    else:
        await msg.answer("Этот файл нельзя заменить")
        logging.info(f"{msg.from_user.id} пытался заменить файл {file_name}")


@router.message(ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID))
async def handle_topic_message(msg: Message, state: FSMContext) -> None:
    """Отправляет сообщение в личный топик пользователя"""

    from app.misc.states import BroadcastStates

    if msg.from_user.is_bot:
        return

    if msg.text and msg.text.startswith("/"):
        await msg.answer("Нет такой команды, но я тебя спас, не бойся")
        return

    if msg.message_thread_id is not None:
        await msg.bot.send_message(
            UserDatabase(topic_id=msg.message_thread_id).tg_id(), text=msg.text
        )
    else:
        if msg.is_from_offline:
            from app.misc import send_broadcast_message

            await send_broadcast_message(msg, state, msg.message_id)
        else:
            await msg.answer(
                "Вы действительно хотите отправить это сообщение?",
                reply_markup=kb.message_confirm(),
            )
            await state.set_state(BroadcastStates.waiting_for_confirmation)
