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
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

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


@router.callback_query(F.data == "confirm_send")
async def confirm_send_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Начинаем отправку сообщений!")
    await state.set_state(BroadcastStates.sending_messages)
    await send_broadcast_message(callback.message, state, callback.message.message_id - 1)
