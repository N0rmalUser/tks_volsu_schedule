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
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import get_schedule, get_today
from app.core.config import config
from app.schemas.enums import ActivityType, Keyboard, Platform, UserRole
from app.services.activity import ActivityService
from app.services.user import UserService
from app.tg.filters import ChatTypeIdFilter
from app.tg.markups import user as kb
from app.tg.markups.admin import admin_menu


router = Router()


@router.message(CommandStart(), ChatTypeIdFilter(chat_type=["private"]))
async def start_handler(msg: Message, session: AsyncSession) -> None:
    """Обработчик команды /start"""

    service = await UserService.create(session, Platform.TELEGRAM, msg.from_user.id)

    topic_id = await service.get_tg_topic_id()
    if not topic_id:
        if msg.from_user.username:
            topic_name = f"{msg.from_user.username} {msg.from_user.id}"
        else:
            topic_name = f"{msg.from_user.full_name} {msg.from_user.id}"
        result = await msg.bot.create_forum_topic(config.admin_chat_id, topic_name)
        topic_id = result.message_thread_id

        await service.set_tg_topic_id(topic_id=topic_id)
        user_info = (
            f"Пользователь: <code>{msg.from_user.full_name}</code>\n"
            f"ID: <code>{msg.from_user.id}</code>\n"
            f"Username: @{msg.from_user.username}\n"
            f"Тип пользователя: {await service.get_user_role()}"
        )
        await msg.bot.send_message(
            config.admin_chat_id,
            message_thread_id=topic_id,
            text=user_info,
            reply_markup=admin_menu(),
            parse_mode=ParseMode.HTML,
        )
        logging.info(f"Создан топик имени {msg.from_user.id} @{msg.from_user.username}")

    role: UserRole = await service.get_user_role()

    menu = kb.teacher_menu() if role == UserRole.TEACHER else kb.student_menu()
    keyboard = kb.get_teachers() if role == UserRole.TEACHER else kb.get_groups()

    await msg.answer(
        f"Привет, {msg.from_user.full_name}\n",
        reply_markup=menu,
    )
    await msg.answer("Выбери себя в списке", reply_markup=keyboard)


@router.message(Command("help"), ChatTypeIdFilter(chat_type=["private"]))
async def help_handler(msg: Message, session: AsyncSession) -> None:
    """Обработчик команды /help. Отправляет сообщение с описанием бота."""

    service = await UserService.create(session, Platform.TELEGRAM, msg.from_user.id)
    role: UserRole = await service.get_user_role()

    if role == UserRole.TEACHER:
        await msg.answer(
            """
Привет, это бот расписания кафедры ТКС!

Кнопка `Расписание на сегодня` показывает расписание на сегодняшний день для выбранного преподавателя.
Кнопки `Группы`, `Преподаватели`, `Кабинеты` открывают соответствующие меню выбора.

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️

Для связи с администратором при возникших ошибках/изменениях в расписании используйте команду /admin и опишите проблему.
""",
        )
    else:
        await msg.answer(
            """
Привет, это бот расписания кафедры ТКС!

Кнопка `Расписание на сегодня` показывает расписание на сегодняшний день для выбранной группы.
Кнопка `Группы` открывает меню выбора групп

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️

Для связи с администратором при возникших ошибках/изменениях в расписании используйте команду /admin и опишите проблему.
Донаты принимаются вкусняшками в 1-19М
""",
        )


@router.message(Command("admin"), ChatTypeIdFilter(chat_type=["private"]))
async def admin_handler(msg: Message, session: AsyncSession) -> None:
    """Обработчик команды /admin. Пересылает сообщение админу и включает слежку за действиями пользователя."""

    service = await UserService.create(session, Platform.TELEGRAM, msg.from_user.id)

    await service.set_tg_tracking(tracking=True)
    topic_id = await service.get_tg_topic_id()
    logging.warning(f"Юзверь {msg.from_user.id} @{msg.from_user.username} просит помощи админа")
    await msg.forward(chat_id=config.admin_chat_id, message_thread_id=topic_id)
    await msg.answer("Модератор скоро напишет вам, ожидайте. Пока можете описать проблему.")
    logging.info(f"{msg.from_user.id} написал админу")


@router.message(Command("spreadsheets"), ChatTypeIdFilter(chat_type=["private"]))
async def spreadsheets_handler(msg: Message, session: AsyncSession) -> None:
    """Обработчик команды /spreadsheets. Присылает пользователю файл с расписанием выбранной группы/преподавателя"""

    service = await UserService.create(session, Platform.TELEGRAM, msg.from_user.id)
    role: UserRole = await service.get_user_role()

    await msg.answer(
        "Выберите, какой тип расписания вы хотите скачать.",
        reply_markup=kb.get_sheets(role),
    )


@router.message(Command("default"), ChatTypeIdFilter(chat_type=["private"]))
async def default_handler(msg: Message, session: AsyncSession) -> None:
    """Устанавливает пользователю преподавателя или группу по-умолчанию"""

    service = await UserService.create(session, Platform.TELEGRAM, msg.from_user.id)
    role: UserRole = await service.get_user_role()

    if role == UserRole.TEACHER:
        await msg.answer("Выберите себя из списка", reply_markup=await kb.get_default_teachers())
    else:
        await msg.answer("Выберите себя из списка", reply_markup=kb.get_default_groups())


@router.message(F.text == "Расписание на сегодня", ChatTypeIdFilter(chat_type=["private"]))
async def schedule_handler(msg: Message, session: AsyncSession) -> None:
    service = await UserService.create(session, Platform.TELEGRAM, msg.from_user.id)
    role: UserRole = await service.get_user_role()
    day, week = get_today()
    entity_id = await service.get_default_id()

    if not entity_id:
        await msg.answer(
            f"Сначала выберите {'ФИО преподавателя' if role == UserRole.TEACHER else 'группу'}, "
            f"нажав на соответствующую кнопку.",
        )
        return

    activity_service = ActivityService(session)
    await activity_service.add(
        user_id=await service.get_id(),
        action=ActivityType.SCHEDULE_VIEW,
        group_id=entity_id,
    )

    if role == UserRole.TEACHER:
        keyboard = Keyboard.TEACHER
        week_kb = kb.get_days(keyboard=keyboard, week=week, day=day, value=entity_id)
    else:
        keyboard = Keyboard.STUDENT
        week_kb = kb.get_days(keyboard=keyboard, week=week, day=day, value=entity_id)

    await msg.answer(
        await get_schedule(
            target=keyboard,
            day=day,
            week=week,
            value=entity_id,
        ),
        reply_markup=week_kb,
    )


@router.message(F.text == "Кабинеты", ChatTypeIdFilter(chat_type=["private"]))
async def rooms_handler(msg: Message) -> None:
    await msg.answer("Выберите кабинет", reply_markup=kb.get_rooms())


@router.message(F.text == "Группы", ChatTypeIdFilter(chat_type=["private"]))
async def groups_handler(msg: Message) -> None:
    await msg.answer("Выберите группу", reply_markup=kb.get_groups())


@router.message(F.text == "Преподаватели", ChatTypeIdFilter(chat_type=["private"]))
async def teachers_handler(msg: Message) -> None:
    await msg.answer("Выберите преподавателя", reply_markup=kb.get_teachers())


@router.message(F.text, ChatTypeIdFilter(chat_type=["private"]))
async def text_handler(msg: Message, session: AsyncSession) -> None:
    service = await UserService.create(session, Platform.TELEGRAM, msg.from_user.id)
    tracked = await service.get_tg_tracking()
    if not tracked:
        logging.info(f"{msg.from_user.id} написал неправильную команду")
        await msg.answer("Я не знаю такой команды")


@router.message(ChatTypeIdFilter(chat_type=["private"]))
async def other_handler(msg: Message, session: AsyncSession) -> None:
    service = await UserService.create(session, Platform.TELEGRAM, msg.from_user.id)
    tracked = await service.get_tg_tracking()
    if not tracked:
        await msg.answer("Я тебя не понимаю, буковы пиши!")
