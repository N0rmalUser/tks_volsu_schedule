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

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.filters import ChatTypeIdFilter
from app.markups import edit_markups as kb
from app.misc.states import NewSchedule

router = Router()


@router.message(ChatTypeIdFilter(chat_type=["private"]), NewSchedule.lesson)
async def lesson_handler(msg: Message, state: FSMContext) -> None:

    data = await state.get_data()
    _, value, _, schedule_id, keyboard_type, _ = data.get("callback_data")
    callback = data.get("callback")
    keyboard = kb.add_group(schedule_id[1], value[1], keyboard_type[1])
    from app.database.schedule import Schedule

    subject_id = Schedule().add_subject(msg.text)
    await callback.message.edit_text("Теперь группу", reply_markup=keyboard)
    await state.clear()


@router.message(ChatTypeIdFilter(chat_type=["private"]), NewSchedule.teacher)
async def teacher_handler(msg: Message, state: FSMContext) -> None:

    data = await state.get_data()
    _, value, _, schedule_id, keyboard_type, _ = data.get("callback_data")
    keyboard = kb.add_group(schedule_id[1], value[1], keyboard_type[1])
    from app.database.schedule import Schedule

    teacher_id = Schedule().add_teacher(msg.text)
    await data.get("callback").message.edit_text("Теперь группу", reply_markup=keyboard)
    await state.clear()


@router.message(ChatTypeIdFilter(chat_type=["private"]), NewSchedule.group)
async def group_handler(msg: Message, state: FSMContext) -> None:

    data = await state.get_data()
    _, value, _, schedule_id, keyboard_type, _ = data.get("callback_data")
    keyboard = kb.add_teacher(schedule_id[1], value[1], keyboard_type[1])
    from app.database.schedule import Schedule

    group_id = Schedule().add_group(msg.text)
    await data.get("callback").message.edit_text("Теперь преподавателя", reply_markup=keyboard)
    await state.clear()


@router.message(ChatTypeIdFilter(chat_type=["private"]), NewSchedule.room)
async def room_handler(msg: Message, state: FSMContext) -> None:

    data = await state.get_data()
    _, value, _, schedule_id, keyboard_type, _ = data.get("callback_data")
    keyboard = kb.add_room(schedule_id[1], value[1], keyboard_type[1])
    await data.get("callback").message.edit_text("Теперь аудиторию", reply_markup=keyboard)
    await state.clear()
