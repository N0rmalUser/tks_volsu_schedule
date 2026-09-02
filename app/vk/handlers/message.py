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

from vkbottle.bot import BotLabeler, Message

from app.common.utils import get_schedule, get_today
from app.database.session import session_scope
from app.schemas.enums import Keyboard, Platform, UserRole
from app.services.user import UserService
from app.vk.markups import days, directions, group_menu, rooms, teacher_menu, teachers


router = BotLabeler()


@router.message(text=["/start", "Начать"])
async def start_handler(msg: Message):
    async with session_scope() as session:
        service = await UserService.create(session, Platform.VK, msg.from_id)
        role = await service.get_user_role()
        if role == UserRole.TEACHER:
            menu = teacher_menu()
            keyboard = teachers()
        else:
            menu = group_menu()
            keyboard = directions()
    await msg.answer(
        message="Привет!\n",
        keyboard=menu,
    )
    await msg.answer(
        message="Выбери себя:",
        keyboard=keyboard,
    )


@router.message(command="help")
async def help_handler(msg: Message):
    await msg.answer(
        """
Привет, это бот расписания кафедры ТКС в вк!

Кнопка `Расписание на сегодня` показывает расписание на сегодняшний день для выбранного преподавателя.
Кнопки `Группы`, `Преподаватели`, `Кабинеты` открывают соответствующие меню выбора.
Из-за ограничения в 10 кнопок, у списка преподавателей добавлены страницы, а у списка групп - разделение по направлениям

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️
""",
    )


@router.message(text="Расписание на сегодня")
async def schedule_handler(msg: Message):
    logging.debug(msg.text)

    async with session_scope() as session:
        service = await UserService.create(session, Platform.VK, msg.from_id)
        role: UserRole = await service.get_user_role()

        day, week = get_today()
        entity_id = await service.get_default_id()

    if not entity_id:
        await msg.answer(
            f"Сначала выберите {'ФИО преподавателя' if role == UserRole.TEACHER else 'группу'}, "
            f"нажав на соответствующую кнопку.",
            keyboard=teachers() if role == UserRole.TEACHER else directions(),
        )
        return

    if role == UserRole.TEACHER:
        keyboard = Keyboard.TEACHER
        week_kb = days(keyboard_type=keyboard, week=week, day=day, value=entity_id)
    else:
        keyboard = Keyboard.STUDENT
        week_kb = days(keyboard_type=keyboard, week=week, day=day, value=entity_id)

    await msg.answer(
        await get_schedule(
            target=keyboard,
            day=day,
            week=week,
            value=entity_id,
        ),
        keyboard=week_kb,
    )


@router.message(text="Кабинеты")
async def rooms_handler(msg: Message):
    await msg.answer("Выберите кабинет", keyboard=rooms())


@router.message(text="Группы")
async def groups_handler(msg: Message) -> None:
    await msg.answer("Выберите группу", keyboard=directions())


@router.message(text="Преподаватели")
async def teachers_handler(msg: Message) -> None:
    await msg.answer("Выберите преподавателя", keyboard=teachers())
