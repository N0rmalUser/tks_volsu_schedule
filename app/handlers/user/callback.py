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
from aiogram.types import CallbackQuery, FSInputFile

from app.config import GROUPS, GROUPS_SCHEDULE_PATH, ROOMS, TEACHERS
from app.database.schedule import Schedule
from app.database.user import User
from app.filters import IgnoreFilter
from app.markups import user as kb
from app.markups.keyboard_factory import (
    ChangeCallbackFactory,
    DayCallbackFactory,
    DefaultChangeCallbackFactory,
)
from app.misc import text_maker, get_today
from app.misc.sheets_maker import room, teacher

router = Router()


@router.callback_query(DayCallbackFactory.filter(IgnoreFilter()))
async def ignore_handler(callback: CallbackQuery) -> None:
    """Функция, сбрасывающая нажатия кнопки без функционала."""

    await callback.answer("Сейчас эта неделя")


async def text_formatter(keyboard_type: str, day: int, week: int, value: int) -> str:
    text = "Ошибка. Напишите админу /admin"

    if keyboard_type == "teacher":
        text = text_maker.get_teacher_schedule(day=day, week=week, teacher_name=Schedule().get_teacher_name(value))
    elif keyboard_type == "group":
        text = text_maker.get_group_schedule(day=day, week=week, group_name=Schedule().get_group_name(value))
    elif keyboard_type == "room":
        text = text_maker.get_room_schedule(day=day, week=week, room_name=Schedule().get_room_name(value))

    return text


@router.callback_query(DayCallbackFactory.filter(F.action == "day" or None))
async def day_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки дня недели. Отправляет расписание на этот день для преподавателей,
    групп и аудиторий."""

    keyboard_type: str = callback_data.keyboard_type
    value: int = callback_data.value
    week: int = callback_data.week
    day: int = callback_data.day

    await callback.message.edit_text(
        await text_formatter(
            keyboard_type=keyboard_type,
            day=day,
            week=week,
            value=value,
        ),
        reply_markup=kb.get_days(keyboard_type=keyboard_type, week=week, day=day, value=value),
    )
    await callback.answer()


@router.callback_query(DayCallbackFactory.filter(F.action == "week" or None))
async def week_handler(callback: CallbackQuery, callback_data: DayCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки недели. Отправляет расписание на следующую неделю для преподавателей,
    групп и аудиторий, сохраняя день."""

    keyboard_type = callback_data.keyboard_type
    value: int = callback_data.value
    week = 1 if int(callback_data.week) != 2 else 2
    day = callback_data.day

    await callback.message.edit_text(
        await text_formatter(
            keyboard_type=keyboard_type,
            day=day,
            week=week,
            value=value,
        ),
        reply_markup=kb.get_days(keyboard_type=keyboard_type, week=week, day=day, value=value),
    )
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "room" or None))
async def room_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки аудитории. Отправляет расписание на этот день для аудитории."""

    day, week = get_today()
    await callback.message.edit_text(
        text_maker.get_room_schedule(
            day=day,
            week=week,
            room_name=Schedule().get_room_name(callback_data.value),
        ),
        reply_markup=kb.get_days(keyboard_type="room", week=week, day=day, value=callback_data.value),
    )
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "teacher" or None))
async def teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки преподавателя. Отправляет расписание на этот день для преподавателя.
    Если преподаватель является учеником (указывается в config.toml), отправляет расписание его групп, смешанное с
    занятиями, которые он сам проводит"""

    user = User(callback.from_user.id)
    user.teacher = callback_data.value
    day, week = get_today()
    await callback.message.edit_text(
        text_maker.get_teacher_schedule(
            day=day,
            week=week,
            teacher_name=Schedule().get_teacher_name(callback_data.value),
        ),
        reply_markup=kb.get_days(
            keyboard_type="teacher",
            week=week,
            day=day,
            value=callback_data.value,
        ),
    )
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "group" or None))
async def group_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Функция, обрабатывающая нажатие кнопки группы. Отправляет расписание на этот день для группы."""

    user = User(callback.from_user.id)
    user.group = callback_data.value
    day, week = get_today()
    await callback.message.edit_text(
        text_maker.get_group_schedule(
            day=day,
            week=week,
            group_name=Schedule().get_group_name(callback_data.value),
        ),
        reply_markup=kb.get_days(
            keyboard_type="group",
            week=week,
            day=day,
            value=callback_data.value,
        ),
    )
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "spreadsheet" or None))
async def spreadsheet_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    if callback_data.value == 1:
        ...
    elif callback_data.value == 2:
        ...
    elif callback_data.value == 3:
        ...
    else:
        await callback.answer("Произошла ошибка, напишите админу /admin")


async def process_default_change(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    """Обработчик изменения значения по умолчанию (teacher/group)."""

    user = User(callback.from_user.id)
    user.default = callback_data.value
    if callback_data.value is None:
        await callback.message.edit_text("Выбор по умолчанию удалён")
        await callback.answer()
        return

    if user.type == "teacher":
        await callback.message.edit_text(
            f"Преподаватель по умолчанию изменён на {Schedule().get_teacher_name(callback_data.value)}"
        )
    else:
        await callback.message.edit_text(
            f"Группа по умолчанию изменена на {Schedule().get_group_name(callback_data.value)}"
        )
    await callback.answer()


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_teacher" or None))
async def default_teacher_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    await process_default_change(callback, callback_data)


@router.callback_query(DefaultChangeCallbackFactory.filter(F.action == "default_group" or None))
async def default_group_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    await process_default_change(callback, callback_data)


@router.callback_query(ChangeCallbackFactory.filter(F.action == "teacher_sheet" or None))
async def teacher_sheet_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    if not callback_data.value:
        await callback.message.edit_text(
            "Выберите преподавателя",
            reply_markup=kb.get_sheet_teachers(callback.from_user.id),
        )
        return
    if callback_data.value == 9999:
        for teacher_name in TEACHERS:
            await callback.message.answer_document(FSInputFile(teacher(teacher_name)))
    else:
        await callback.message.answer_document(FSInputFile(teacher(Schedule().get_teacher_name(callback_data.value))))
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "group_sheet" or None))
async def group_sheet_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    if not callback_data.value:
        await callback.message.edit_text("Выберите группу", reply_markup=kb.get_sheet_groups(callback.from_user.id))
        return
    if callback_data.value == 9999:
        for group in GROUPS:
            await callback.message.answer_document(FSInputFile(GROUPS_SCHEDULE_PATH / f"{group}.docx"))
    else:
        group_name = Schedule().get_group_name(callback_data.value)
        file_path = GROUPS_SCHEDULE_PATH / f"{group_name}.docx"
        if not file_path.exists():
            prefix, number = group_name.split("-")  # напр. "ИТСб", "251"
            if number.endswith("1"):
                paired_number = number[:-1] + "2"
                candidate = GROUPS_SCHEDULE_PATH / f"{prefix}-{number} {paired_number}.docx"
                if candidate.exists():
                    file_path = candidate
            elif number.endswith("2"):
                paired_number = number[:-1] + "1"
                candidates = [
                    f"{prefix}-{number} {paired_number}.docx",
                    f"{prefix}-{paired_number} {number}.docx",
                    f"{prefix}-{number}_{paired_number}.docx",
                    f"{prefix}-{paired_number}_{number}.docx",
                ]
                for candidate_name in candidates:
                    candidate_path = GROUPS_SCHEDULE_PATH / candidate_name
                    if candidate_path.exists():
                        file_path = candidate_path
                        break
        await callback.message.answer_document(FSInputFile(file_path))
    await callback.answer()


@router.callback_query(ChangeCallbackFactory.filter(F.action == "room_sheet" or None))
async def room_sheet_handler(callback: CallbackQuery, callback_data: ChangeCallbackFactory) -> None:
    if not callback_data.value:
        await callback.message.edit_text("Выберите аудиторию", reply_markup=kb.get_sheet_rooms())
        return
    if callback_data.value == 9999:
        for room_name in ROOMS:
            await callback.message.answer_document(FSInputFile(room(room_name)))
    else:
        await callback.message.answer_document(FSInputFile(room(Schedule().get_room_name(callback_data.value))))
    await callback.answer()
