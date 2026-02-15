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

from app.common import get_today, text_maker
from app.database import User
from app.database.schedule import Schedule
from app.vk import markups

router = BotLabeler()

@router.message(command='start')
async def start_handler(msg: Message):
    await msg.answer(
        message="Привет!\n",
        keyboard=markups.menu(),
    )

@router.message(command='help')
async def help_handler(msg: Message):
    await msg.answer(
            """
Привет, это бот расписания кафедры ТКС!

Кнопка `Расписание на сегодня` показывает расписание на сегодняшний день для выбранного преподавателя.
Кнопки `Группы`, `Преподаватели`, `Кабинеты` открывают соответствующие меню выбора.

Если у группы номер `ИБТС-231.2` - это 2-я подгруппа, если `.2` отсутствует, идут обе подгруппы

✅ показывает, что выбрана эта неделя, для изменения недели нужно нажать кнопку с ➡️
"""
    )

@router.message(text="Расписание на сегодня")
async def schedule_handler(msg: Message):
    user = User(msg.chat_id)
    day, week = get_today()

    entity_id: int = user.teacher if user.type == "teacher" else user.group

    if not entity_id:
        await msg.answer(
            f"Сначала выберите {'ФИО преподавателя' if user.type == 'teacher' else 'группу'}, "
            f"нажав на соответствующую кнопку.",
            keyboard=markups.days(keyboard_type="group" if user.type == "student" else "teacher", week=week, day=day, value=entity_id)
        )
        return

    if user.type == "teacher":
        week_kb = markups.days(keyboard_type="teacher", week=week, day=day, value=entity_id)
        print(week_kb)
        await msg.answer(
            text_maker.get_teacher_schedule(
                day=day,
                week=week,
                teacher_name=Schedule().get_teacher_name(entity_id),
            ),
            keyboard=week_kb,
        )
    elif user.type == "student":
        week_kb = markups.days(keyboard_type="group", week=week, day=day, value=entity_id)
        print(week_kb)
        await msg.answer(
            text_maker.get_group_schedule(
                day=day,
                week=week,
                group_name=Schedule().get_group_name(entity_id),
            ),
            keyboard=week_kb,
        )
    else:
        logging.info(f"{msg.from_user.id} неправильный тип пользователя")
        await msg.answer("Ошибка! Напишите админу /admin")

@router.message(text="Кабинеты")
async def rooms_handler(msg: Message):
    await msg.answer("Выберите кабинет", keyboard=markups.rooms())


@router.message(text="Группы")
async def groups_handler(msg: Message) -> None:
    await msg.answer("Выберите группу",  keyboard=markups.groups())


@router.message(text="Преподаватели")
async def teachers_handler(msg: Message) -> None:
    await msg.answer("Выберите преподавателя",  keyboard=markups.teachers())
