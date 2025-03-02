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
from aiogram.filters.chat_member_updated import KICKED, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from app import ADMIN_CHAT_ID
from app.database.user import User

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания блокировки бота пользователем."""

    user = User(event.from_user.id)
    user.blocked = True
    await event.bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id,
                                 text=f"Пользователь @{event.from_user.username} заблокировал бота")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания разблокировки бота пользователем."""

    user = User(event.from_user.id)
    user.blocked = False
    await event.bot.send_message(ADMIN_CHAT_ID, message_thread_id=user.topic_id,
                                 text=f"Пользователь @{event.from_user.username} разблокировал бота")
