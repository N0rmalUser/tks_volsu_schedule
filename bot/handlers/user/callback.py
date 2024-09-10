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

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.database.schedule import Schedule
from bot.database.user import UserDatabase
from bot.markups import user_markups as kb
from bot.markups.keyboard_factory import (
    ChangeCallbackFactory,
    DayCallbackFactory,
    DefaultChangeCallbackFactory,
)
from bot.misc import text_maker

router = Router()


@router.callback_query(DayCallbackFactory.filter(F.action == "ignore"))
async def ignore_handler(callback: CallbackQuery) -> None:
    """Функция, сбрасывающая нажатия кнопки без функционала."""

    await callback.answer("Сейчас эта неделя")


@router.callback_query(DayCallbackFactory.filter(F.action == "day"))
async def day_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки дня недели. Отправляет расписание на этот день для преподавателей, групп и аудиторий."""

    from bot.bot import bot
    from bot.config import ADMIN_CHAT_ID

    keyboard_type: str = callback_data.keyboard_type
    value: int = callback_data.value
    week: int = callback_data.week
    day: int = callback_data.day

    user = UserDatabase(callback.from_user.id)

    if callback_data.day == user.day:
        await callback.answer()
        return
    user.day = callback_data.day
    user.week = week
    text = "Ошибка. Напишите админу /admin"

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(
            day=day, week=week, teacher_name=Schedule().get_teacher_name(value)
        )
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(
            day=day, week=week, group_name=Schedule().get_group_name(value)
        )
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(
            day=day, week=week, room_name=Schedule().get_room_name(value)
        )

    if user.type == "teacher":
        week_kb = kb.get_days_teacher(
            callback.from_user.id, keyboard_type=keyboard_type, week=week, value=value
        )
    else:
        week_kb = kb.get_days(
            callback.from_user.id, keyboard_type=keyboard_type, week=week, value=value
        )

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()

    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data)


@router.callback_query(DayCallbackFactory.filter(F.action == "week"))
async def week_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки недели. Отправляет расписание на следующую неделю для преподавателей, групп и аудиторий, сохраняя день."""

    from bot.bot import bot
    from bot.config import ADMIN_CHAT_ID

    keyboard_type = callback_data.keyboard_type
    value: int = callback_data.value
    week = 1 if int(callback_data.week) != 2 else 2
    day = callback_data.day

    user = UserDatabase(callback.from_user.id)

    if callback_data.day == str(user.day):
        await callback.answer()
        return
    user.set_day = callback_data.day
    user.week = week
    text = "Ошибка. Напишите админу /admin"

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(
            day=day, week=week, teacher_name=Schedule().get_teacher_name(value)
        )
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(
            day=day, week=week, group_name=Schedule().get_group_name(value)
        )
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(
            day=day, week=week, room_name=Schedule().get_room_name(value)
        )

    if user.type == "teacher":
        week_kb = kb.get_days_teacher(
            callback.from_user.id, keyboard_type=keyboard_type, week=week, value=value
        )
    else:
        week_kb = kb.get_days(
            callback.from_user.id, keyboard_type=keyboard_type, week=week, value=value
        )

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()

    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data)

    await callback.message.edit_text(text, reply_markup=week_kb)
    await callback.answer()

    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data)


@router.callback_query(ChangeCallbackFactory.filter(F.action == "room"))
async def room_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки аудитории. Отправляет расписание на этот день для аудитории."""

    from bot.bot import bot
    from bot.config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()

    if user.type == "teacher":
        week_kb = kb.get_days_teacher(
            callback.from_user.id,
            keyboard_type="room",
            week=user.week,
            value=callback_data.value,
        )
    else:
        week_kb = kb.get_days(
            callback.from_user.id,
            keyboard_type="room",
            week=user.week,
            value=callback_data.value,
        )
    await callback.message.edit_text(
        text_maker.get_room_schedule(
            day=user.day,
            week=user.week,
            room_name=Schedule().get_room_name(callback_data.value),
        ),
        reply_markup=week_kb,
    )
    await callback.answer()

    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data)


@router.callback_query(ChangeCallbackFactory.filter(F.action == "teacher"))
async def teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки преподавателя. Отправляет расписание на этот день для преподавателя.
    Если преподаватель является учеником (указывается в config.toml), отправляет расписание его групп, смешанное с занятиями, которые он сам проводит
    """

    from bot.bot import bot
    from bot.config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()
    user.teacher = callback_data.value

    if user.type == "teacher":
        week_kb = kb.get_days_teacher(
            callback.from_user.id,
            keyboard_type="teacher",
            week=user.week,
            value=callback_data.value,
        )
    else:
        week_kb = kb.get_days(
            callback.from_user.id,
            keyboard_type="teacher",
            week=user.week,
            value=callback_data.value,
        )
    await callback.message.edit_text(
        text_maker.get_teacher_schedule(
            day=user.day,
            week=user.week,
            teacher_name=Schedule().get_teacher_name(callback_data.value),
        ),
        reply_markup=week_kb,
    )
    await callback.answer()
    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data)


@router.callback_query(ChangeCallbackFactory.filter(F.action == "group"))
async def group_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки группы. Отправляет расписание на этот день для группы."""

    from bot.bot import bot
    from bot.config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.set_today_date()
    user.group = callback_data.value

    if user.type == "teacher":
        week_kb = kb.get_days_teacher(
            callback.from_user.id,
            keyboard_type="group",
            week=user.week,
            value=callback_data.value,
        )
    else:
        week_kb = kb.get_days(
            callback.from_user.id,
            keyboard_type="group",
            week=user.week,
            value=callback_data.value,
        )

    await callback.message.edit_text(
        text_maker.get_group_schedule(
            day=user.day,
            week=user.week,
            group_name=Schedule().get_group_name(callback_data.value),
        ),
        reply_markup=week_kb,
    )
    await callback.answer()

    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data)


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_teacher"))
async def default_teacher_handler(
        callback: CallbackQuery, callback_data: ChangeCallbackFactory
) -> None:
    from bot.bot import bot
    from bot.config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.default = callback_data.value

    await callback.message.edit_text(f"Default изменён на {callback_data.value}")
    await callback.answer()

    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data)


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_group"))
async def default_group_handler(
        callback: CallbackQuery, callback_data: ChangeCallbackFactory
) -> None:
    from bot.bot import bot
    from bot.config import ADMIN_CHAT_ID

    user = UserDatabase(callback.from_user.id)
    user.default = callback_data.value

    await callback.message.edit_text(f"Default изменён на {callback_data.value}")
    await callback.answer()

    if user.tracking:
        await bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id, text=callback.data)
