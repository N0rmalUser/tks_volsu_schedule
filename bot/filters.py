from aiogram.filters import BaseFilter
from aiogram import types
from config import ADMIN_CHAT_ID


class ChatTypeIdFilter(BaseFilter):
    """Фильтр, проверяющий тип чата и id, если указан, и возвращающий True или False"""
    def __init__(self, chat_type: list, chat_id: int = None):
        self.chat_id = chat_id
        self.chat_type = chat_type

    async def __call__(self, message: types.Message) -> bool:
        if not bool(message.from_user.is_bot):
            if message.chat.type in self.chat_type and self.chat_id is not None:
                return str(message.chat.id) == str(ADMIN_CHAT_ID)
            return message.chat.type == self.chat_type



