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
import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database import User, get_users_by_teacher_id, all_user_ids, student_ids, teachers_ids
from app.database.schedule import Schedule
from app.misc import send_broadcast_message
from app.misc.states import BroadcastStates

router = Router()


@router.callback_query(F.data == "cancel_send")
async def confirm_send(callback_query: CallbackQuery):
    await callback_query.answer("Отправка отменена.")
    await callback_query.message.delete()


@router.callback_query(F.data == "cancel_sending")
async def cancel_sending(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastStates.cancel_sending)
    await callback.answer("Отправка будет остановлена.")
    await callback.message.delete_reply_markup()


@router.callback_query(F.data == "confirm_all")
async def confirm_send_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Начинаем отправку сообщений всем!")
    await state.set_state(BroadcastStates.sending_messages)
    await send_broadcast_message(callback.message, state, callback.message.message_id - 1, all_user_ids())


@router.callback_query(F.data == "confirm_students")
async def confirm_send_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Начинаем отправку сообщений студентам!")
    await state.set_state(BroadcastStates.sending_messages)
    await send_broadcast_message(callback.message, state, callback.message.message_id - 1, student_ids())

@router.callback_query(F.data == "confirm_teachers")
async def confirm_send_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Начинаем отправку сообщений преподавателям!")
    await state.set_state(BroadcastStates.sending_messages)
    await send_broadcast_message(callback.message, state, callback.message.message_id - 1, teachers_ids())

@router.callback_query(F.data == "notify")
async def find_groups_handler(callback: CallbackQuery):
    from app.database import get_users_by_group_id

    await callback.answer()

    found_groups = re.findall(r"(\w+-\d{3}(_\d)?)", callback.message.text)
    found_teachers = re.findall(r"расписание_занятий_(\w+_\w[.|_]\w\.)", callback.message.text)
    users = 0
    if len(found_groups) > 0:
        for group in found_groups:
            group_id: int = Schedule().get_group_id(group[0])
            for user_id in get_users_by_group_id(group_id):
                user = User(user_id)
                if not user.blocked and not user.banned:
                    await callback.bot.send_message(
                        user_id, f"Обновлено расписание для {group[0]}"
                    )
                    users += 1
                    await asyncio.sleep(1)
    elif len(found_teachers) > 0:
        for teacher in found_teachers:
            teacher = re.sub(r"_", r".", re.sub(r"([А-ЯЁа-яё]{2,})_", r"\1 ", teacher))
            teacher_id: int = Schedule().get_teacher_id(teacher)
            for user_id in get_users_by_teacher_id(teacher_id):
                user = User(user_id)
                if not user.blocked and not user.banned:
                    await callback.bot.send_message(user_id, f"Обновлено расписание для {teacher}")
                    users += 1
                    await asyncio.sleep(1)
    await callback.message.edit_text(f"Оповещено пользователей: {users}")
