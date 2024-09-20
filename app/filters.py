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

from aiogram import types
from aiogram.filters import BaseFilter

from app.config import ADMIN_CHAT_ID


class ChatTypeIdFilter(BaseFilter):
    """Фильтр, проверяющий тип чата и id, если указан, и возвращающий True или False"""

    def __init__(self, chat_type: list, chat_id: int = None):
        self.chat_id = chat_id
        self.chat_type = chat_type

    async def __call__(self, message: types.Message) -> bool:
        if not bool(message.from_user.is_bot):
            if message.chat.type in self.chat_type and self.chat_id is not None:
                return str(message.chat.id) == str(ADMIN_CHAT_ID)
            return message.chat.type in self.chat_type
