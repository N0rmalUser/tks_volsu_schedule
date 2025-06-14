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

import asyncio
import logging
import os

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
    DATA_PATH,
    GROUPS_SCHEDULE_PATH,
    LOG_FILE,
    PLOT_PATH,
    SCHEDULE_DB,
    USERS_DB
)
from app.database import get_all_users_info, get_tracked_users, tracking_manage, user_info
from app.database.user import User
from app.filters import ChatTypeIdFilter
from app.markups import admin as kb

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
            user_id=User(topic_id=msg.message_thread_id).id,
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
            user_id=User(topic_id=msg.message_thread_id).id, date_str=date
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
    user = User(topic_id=msg.message_thread_id)
    user.banned = True
    await msg.answer("Мы его забанили!!!")
    await msg.bot.send_message(user.id, "За нарушение правил, тебя забанили")
    logging.info(f"Забанен юзверь {user.id}")


@router.message(
    Command("unban"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def ban_command_handler(msg: Message) -> None:
    """Разбанивает пользователя. Изменяет значение столбца banned в базе данных."""

    user = User(topic_id=msg.message_thread_id)
    user.banned = False
    await msg.answer("Мы его разбанили!!!")
    await msg.bot.send_message(user.id, "Амнистия! Тебя разбанили")
    logging.info(f"Разбанен юзверь {user.id}")


@router.message(
    Command("clear"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def dump_handler(msg: Message) -> None:
    """Удаляет все файлы расписания."""

    start = await msg.answer("Удаляю ненужные файлы")
    for i in (GROUPS_SCHEDULE_PATH, COLLEGE_SHEETS_PATH):
        for filename in os.listdir(i):
            file_path = os.path.join(COLLEGE_SHEETS_PATH, filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logging.error(e)
    await start.edit_text("Ненужные файлы удалены")



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

    data = {
        "hash": "query_id=AAHkr7QcAAAAAOSvtBw41eSu&user=%7B%22id%22%3A481603556%2C%22first_name%22%3A%22%D0%92%D0%BE%D0%B2%D0%B0%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22n0rmal_user%22%2C%22language_code%22%3A%22ru%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FMwzX7xhSh8lSg8JRGT7onqJJW5SbzCNkVvjAJeudEpE.svg%22%7D&auth_date=1748944069&signature=oo8rRuRrNBDO02--MQR7gxWDrm5IOy-RsdTwFxD9Lmw6_3pKEuL5yTxRtYVXP1FUHhQMv0oPl1_Ok1VJ13PzBg&hash=d6d69c82f0b8bae1f3b1941536e88f13c6b255eeb0ec53d5daa3f34d3f57f3bf",
        "start": "download"
    }

    total = len(COLLEGE_TEACHERS)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20, ssl=False)) as session:
        try:
            for index, (teacher_name, teacher_id) in enumerate(COLLEGE_TEACHERS.items()):
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        request_data = {**data, "teacherId": teacher_id}
                        async with session.post(
                                url="https://app.volsu.ru/api/bot/select-teacher",
                                json=request_data
                        ) as response:
                            print(f"{response.ok} {index + 1} из {total} (Попытка {attempt + 1}/{max_retries})")
                            if response.ok:
                                break
                            await asyncio.sleep(5)
                    except Exception as e:
                        print(
                            f"Ошибка при отправке запроса для {teacher_name} ({teacher_id}): {e} (Попытка {attempt + 1}/{max_retries})")
                        await asyncio.sleep(1)
                else:
                    print(f"Не удалось выполнить запрос для {teacher_name} ({teacher_id}) после {max_retries} попыток")
                await asyncio.sleep(1)
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
        schedule_parser.university_schedule_parser()
    except Exception as e:
        await start.edit_text("Ошибка обновления базы данных расписания университета")
        logging.error(e)
        return

    try:
        schedule_parser.college_schedule_parser()
    except Exception as e:
        await start.edit_text("Ошибка обновления базы данных расписания колледжа")
        logging.error(e)
        return

    await start.edit_text("База данных расписания обновлена")
    logging.info("База данных расписания обновлена")


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
        user = User(topic_id=msg.message_thread_id)
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
                text=user_info(User(topic_id=msg.message_thread_id).id),
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
        user = User(topic_id=msg.message_thread_id)
        user.type = "teacher"
        await start.edit_text("Тип пользователя изменён на `teacher`")


@router.message(
    Command("student"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_student(msg: Message) -> None:
    start = await msg.answer("Изменяю тип пользователя...")
    if start.message_thread_id:
        user = User(topic_id=msg.message_thread_id)
        user.type = "student"
        await start.edit_text("Тип пользователя изменён на `student`")


@router.message(
    F.document,
    ChatTypeIdFilter(chat_type=["group", "supergroup"]),
)
async def file_handler(msg: Message):
    """Ловит документы и заменяет файл schedule.db, users.db, activities.db на полученные."""

    file_name = msg.document.file_name
    file_map = {
        "schedule.db": {
            "path": DATA_PATH / "db",
            "message": "Заменили расписание",
        },
        "users.db": {
            "path": DATA_PATH / "db",
            "message": "Заменили базу данных пользователей",
        },
        "activities.db": {
            "path": DATA_PATH / "db",
            "message": "Заменили базу данных активности пользователей",
        },
        ".xlsx": {
            "path": COLLEGE_SHEETS_PATH,
            "message": file_name,
        },
        ".docx": {
            "path": GROUPS_SCHEDULE_PATH,
            "message": file_name,
        },
    }

    key = next((key for key in file_map if key in file_name), None)
    try:
        if key:
            file_id = msg.document.file_id
            file_info = await msg.bot.get_file(file_id)
            downloaded_file = await msg.bot.download_file(file_info.file_path)

            with open(file_map[key]["path"] / file_name, "wb") as new_file:
                new_file.write(downloaded_file.read())

            if not hasattr(msg.bot, "collected_messages"):
                msg.bot.collected_messages = []

            msg.bot.collected_messages.append(file_map[key]["message"])
            logging.info(file_map[key]["message"])

        else:
            if not hasattr(msg.bot, "collected_messages"):
                msg.bot.collected_messages = []
            msg.bot.collected_messages.append(f"Файл {file_name} нельзя заменить")
            logging.info(f"{msg.from_user.id} пытался заменить файл {file_name}")

        if hasattr(msg.bot, "send_message_task"):
            msg.bot.send_message_task.cancel()

        msg.bot.send_message_task = asyncio.create_task(send_collected_messages(msg))
    except Exception:
        pass


async def send_collected_messages(msg: Message):
    await asyncio.sleep(5)

    if hasattr(msg.bot, "collected_messages") and msg.bot.collected_messages:
        await msg.answer(
            "Заменил файлы:\n" + "\n".join(msg.bot.collected_messages), reply_markup=kb.notify()
        )
        del msg.bot.collected_messages


@router.message(ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID))
async def handle_topic_message(msg: Message, state: FSMContext) -> None:
    """Отправляет сообщение в личный топик пользователя"""

    from app.misc.states import BroadcastStates

    if msg.from_user.is_bot:
        return

    if msg.text and (msg.text.startswith("/") or msg.text.startswith(".")):
        await msg.answer("Нет такой команды, но я тебя спас, не бойся")
        return

    if msg.message_thread_id is not None:
        await msg.bot.copy_message(
            chat_id=User(topic_id=msg.message_thread_id).id,
            from_chat_id=msg.chat.id,
            message_id=msg.message_id,
        )
    else:
        if msg.is_from_offline:
            from app.misc import send_broadcast_message

            await send_broadcast_message(msg, state, msg.message_id)
        else:
            await msg.answer(
                "Кому отправить это сообщений?",
                reply_markup=kb.message_confirm(),
            )
            await state.set_state(BroadcastStates.waiting_for_confirmation)
