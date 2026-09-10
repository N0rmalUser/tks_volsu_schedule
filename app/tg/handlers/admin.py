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

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schedule_parser import parse_university_schedule
from app.common.user import user_info
from app.core.config import config
from app.core.constants import GROUPS_SCHEDULE_PATH
from app.schemas.enums import GroupType, UserRole
from app.services.schedule import ScheduleService
from app.services.user import UserService
from app.tg.filters import ChatTypeIdFilter
from app.tg.markups import admin as kb


router = Router()
log = logging.getLogger(__name__)


@router.message(Command("menu"), ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=config.admin_chat_id))
async def menu_command_track(msg: Message) -> None:
    await msg.answer("Меню админа", reply_markup=kb.admin_menu())


@router.message(Command("update"), ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=config.admin_chat_id))
async def update_handler(msg: Message) -> None:

    start = await msg.answer("Обновляю расписание университета...")
    try:
        rows = parse_university_schedule()

        await ScheduleService().import_schedule(
            rows=rows,
            group_type=GroupType.UNIVERSITY,
        )
    except Exception:
        await start.edit_text("Ошибка обновления базы данных расписания университета")
        log.exception("schedule.database_update_failed")
        return

    await start.edit_text("База данных расписания обновлена")
    log.info("schedule.updated")


@router.message(Command("track"), ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=config.admin_chat_id))
async def track_command_handler(msg: Message, command: CommandObject, session: AsyncSession) -> None:
    """Включает/выключает трекинг для пользователя или для всех пользователей."""

    if command.args is None:
        await msg.answer("Ошибка: не переданы аргументы")
        return

    command = str(command.args).lower()
    start = await msg.answer("Подождите...")

    if start.message_thread_id:
        service = await UserService.from_tg_topic(session, tg_topic_id=start.message_thread_id)
        if service:
            if command == "start":
                await service.set_tg_tracking(True)
            elif command == "stop":
                await service.set_tg_tracking(False)
            elif command == "status":
                pass
            tracked = await service.get_tg_tracking()
            await start.edit_text(f"Трекинг {'включен' if tracked else 'выключен'}")


@router.message(Command("info"), ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=config.admin_chat_id))
async def info_command_handler(msg: Message, session: AsyncSession) -> None:
    """Присылает информацию о пользователе топика"""

    start = await msg.answer(text="Собираю статистику")
    if start.message_thread_id:
        service = await UserService.from_tg_topic(session, tg_topic_id=start.message_thread_id)
        if not service:
            return
        user_id = await service.get_user_id()
        if user_id:
            await start.edit_text(
                text=await user_info(service),
                parse_mode="HTML",
            )


@router.message(Command("teacher"), ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=config.admin_chat_id))
async def teacher_command_handler(msg: Message, session: AsyncSession) -> None:
    start = await msg.answer("Изменяю тип пользователя...")
    if start.message_thread_id:
        service = await UserService.from_tg_topic(session, tg_topic_id=start.message_thread_id)
        if not service:
            return
        await service.set_user_role(UserRole.TEACHER)
        await start.edit_text("Тип пользователя изменён на `teacher`")


@router.message(Command("student"), ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=config.admin_chat_id))
async def student_command_handler(msg: Message, session: AsyncSession) -> None:
    start = await msg.answer("Изменяю тип пользователя...")
    if start.message_thread_id:
        service = await UserService.from_tg_topic(session, tg_topic_id=start.message_thread_id)
        if not service:
            return
        await service.set_user_role(UserRole.STUDENT)
        await start.edit_text("Тип пользователя изменён на `student`")


@router.message(F.document, ChatTypeIdFilter(chat_type=["group", "supergroup"]))
async def file_handler(msg: Message) -> None:
    """Ловит документы и заменяет файл schedule.db, users.db, activities.db на полученные."""

    file_name = msg.document.file_name
    file_map = {
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

            file_path = file_map[key]["path"] / file_name

            with file_path.open("wb") as new_file:
                new_file.write(downloaded_file.read())

            if not hasattr(msg.bot, "collected_messages"):
                msg.bot.collected_messages = []

            msg.bot.collected_messages.append(file_map[key]["message"])
        else:
            if not hasattr(msg.bot, "collected_messages"):
                msg.bot.collected_messages = []
            msg.bot.collected_messages.append(f"Файл {file_name} нельзя заменить")

        if hasattr(msg.bot, "send_message_task"):
            msg.bot.send_message_task.cancel()

        msg.bot.send_message_task = asyncio.create_task(send_collected_messages(msg))
    except Exception:
        log.exception("schedule.file_change_error")


async def send_collected_messages(msg: Message) -> None:
    await asyncio.sleep(5)

    if hasattr(msg.bot, "collected_messages") and msg.bot.collected_messages:
        await msg.answer("Заменил файлы:\n" + "\n".join(msg.bot.collected_messages))
        log.info("schedule.files_changed")
        del msg.bot.collected_messages


@router.message(ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=config.admin_chat_id))
async def topic_message_handler(msg: Message, session: AsyncSession) -> None:
    """Отправляет сообщение в личный топик пользователя"""

    if msg.from_user.is_bot:
        return

    if msg.text and (msg.text.startswith("/") or msg.text.startswith(".")):
        await msg.answer("Нет такой команды, но я тебя спас, не бойся")
        return

    if msg.message_thread_id:
        service = await UserService.from_tg_topic(session, tg_topic_id=msg.message_thread_id)
        user_id = await service.get_user_id()
        await msg.bot.copy_message(
            chat_id=user_id,
            from_chat_id=msg.chat.id,
            message_id=msg.message_id,
        )
