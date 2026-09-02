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
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils import get_schedule, get_today
from app.schemas.enums import ActivityType, Keyboard, Platform, WeekType
from app.services.activity import ActivityService
from app.services.schedule import ScheduleService
from app.services.user import UserService
from app.tg.filters import IgnoreFilter
from app.tg.markups import user as kb
from app.tg.markups.keyboard_factory import (
    ChangeCallbackFactory,
    DayCallbackFactory,
    DefaultChangeCallbackFactory,
)


router = Router()


@router.callback_query(DayCallbackFactory.filter(IgnoreFilter()))
async def ignore_handler(callback: CallbackQuery) -> None:
    """Функция, сбрасывающая нажатия кнопки без функционала."""

    await callback.answer("Сейчас эта неделя")


@router.callback_query(DayCallbackFactory.filter(F.action.in_(["day", "week"])))
async def day_handler(callback: CallbackQuery, callback_data: DayCallbackFactory, session: AsyncSession) -> None:
    """Функция, обрабатывающая нажатие кнопки дня недели. Отправляет расписание на этот день для преподавателей,
    групп и аудиторий."""

    value: int = callback_data.value
    week: WeekType = callback_data.week
    day: int = callback_data.day
    keyboard: Keyboard = callback_data.keyboard

    user = await UserService.create(session, Platform.TELEGRAM, callback.from_user.id)
    user_id = await user.get_id()
    service = ActivityService(session)
    await service.add(
        user_id=user_id,
        action=ActivityType.DAY_VIEW,
        group_id=value,
    )

    if callback_data.action == "week":
        week: WeekType = WeekType.ODD if callback_data.week != WeekType.EVEN else WeekType.EVEN

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_days(keyboard=keyboard, week=week, day=day, value=value),
    )
    await callback.answer()


@router.callback_query(DayCallbackFactory.filter(F.action == "week"))
async def week_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки недели. Отправляет расписание на следующую неделю для преподавателей,
    групп и аудиторий, сохраняя день."""

    value: int = callback_data.value
    week: WeekType = WeekType.ODD if callback_data.week != WeekType.EVEN else WeekType.EVEN
    day: int = callback_data.day
    keyboard: Keyboard = callback_data.keyboard

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_days(keyboard=keyboard, week=week, day=day, value=value),
    )
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "room"))
async def room_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки аудитории. Отправляет расписание на этот день для аудитории."""

    value: int = callback_data.value
    day, week = get_today()
    keyboard = Keyboard.ROOM

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_days(keyboard=keyboard, week=week, day=day, value=value),
    )
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action.in_(["group", "teacher"])))
async def group_teacher_handler(
    callback: CallbackQuery, callback_data: ChangeCallbackFactory, session: AsyncSession
) -> None:
    """Функция, обрабатывающая нажатие кнопок группы и преподавателя. Отправляет расписание на этот день для группы или
    преподавателя. Если преподаватель является учеником (указывается в core.toml), отправляет расписание его групп,
    смешанное с занятиями, которые он сам проводит"""

    value: int = callback_data.value
    day, week = get_today()

    service = await UserService.create(session, Platform.TELEGRAM, callback.from_user.id)

    if callback_data.action == "teacher":
        await service.set_teacher(value)
        keyboard = Keyboard.TEACHER
    else:
        await service.set_group(value)
        keyboard = Keyboard.STUDENT

    text = await get_schedule(
        target=keyboard,
        day=day,
        week=week,
        value=value,
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=kb.get_days(
            keyboard=keyboard,
            week=week,
            day=day,
            value=value,
        ),
    )
    await callback.answer()


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_teacher"))
async def default_teacher_handler(
    callback: CallbackQuery, callback_data: DefaultChangeCallbackFactory, session: AsyncSession
) -> None:
    value: int = callback_data.value
    if value is None:
        await callback.message.edit_text("Выбор по умолчанию удалён")
        await callback.answer()
        return

    service = await UserService.create(session, Platform.TELEGRAM, callback.from_user.id)
    await service.set_default_id(value)
    await callback.message.edit_text(
        f"Преподаватель по умолчанию изменён на {await ScheduleService().get_teacher_name(value)}",
    )
    await callback.answer()


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_group"))
async def default_group_handler(
    callback: CallbackQuery, callback_data: DefaultChangeCallbackFactory, session: AsyncSession
) -> None:
    value: int = callback_data.value
    if value is None:
        await callback.message.edit_text("Выбор по умолчанию удалён")
        await callback.answer()
        return

    service = await UserService.create(session, Platform.TELEGRAM, callback.from_user.id)

    await service.set_default_id(value)
    await callback.message.edit_text(
        f"Группа по умолчанию изменена на {await ScheduleService().get_group_name(value)}",
    )
    await callback.answer()
